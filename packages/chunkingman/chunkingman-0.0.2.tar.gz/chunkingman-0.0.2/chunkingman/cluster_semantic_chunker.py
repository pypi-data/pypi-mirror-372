from __future__ import annotations

from typing import Any, Callable, List, Optional, Tuple
import os
import numpy as np
import tiktoken

# Dependencias locales
from .base_chunker import BaseChunker
from .recursive_token_chunker import RecursiveTokenChunker
from .utils import get_openai_embedding_function, openai_token_count


class ClusterSemanticChunker(BaseChunker):
    """Chunker semántico basado en:
    1) pre-segmentación por tokens (recursiva)
    2) embeddings + matriz de similitud (coseno)
    3) programación dinámica (DP) para segmentación óptima con penalización

    Parámetros clave:
        embedding_function: callable(List[str]) -> List[List[float]]
        max_chunk_size: límite superior de tokens por chunk final
        min_chunk_size: tamaño objetivo de los "pre-chunks" para construir la matriz
        length_function: función para contar tokens (por defecto, cl100k_base)
        batch_size: tamaño de lote para calcular embeddings
        lambda_penalty: penalización por cada cluster en la DP (controla sobre-segmentación)
        similarity_band: si se especifica (int), se atenúan similitudes |i-j| > band
    """

    def __init__(
        self,
        embedding_function: Optional[Callable[[List[str]], List[List[float]]]] = None,
        max_chunk_size: int = 800,
        min_chunk_size: int = 140,
        length_function: Callable[[str], int] = openai_token_count,
        batch_size: int = 256,
        lambda_penalty: float = 5.0,
        similarity_band: Optional[int] = None,
    ) -> None:
        if embedding_function is None:
            embedding_function = get_openai_embedding_function()

        # Pre-splitter por tokens (mantiene separadores, controla tamaño real)
        self.splitter = RecursiveTokenChunker(
            chunk_size=min_chunk_size,
            chunk_overlap=0,
            length_function=length_function,
            separators=["\n\n", "\n", ".", "?", "!", " ", ""],
        )

        self._chunk_size = int(max_chunk_size)
        self._min_chunk_size = int(min_chunk_size)
        self.embedding_function = embedding_function
        self._length_function = length_function
        self._batch_size = int(batch_size)
        self._lambda = float(lambda_penalty)
        self._band = similarity_band

    # ------------------------------ Utils ---------------------------------
    @staticmethod
    def _l2_normalize(E: np.ndarray) -> np.ndarray:
        norms = np.linalg.norm(E, axis=1, keepdims=True) + 1e-12
        return E / norms

    def _batched_embeddings(self, sentences: List[str]) -> np.ndarray:
        N = len(sentences)
        embs: List[np.ndarray] = []
        for i in range(0, N, self._batch_size):
            batch = sentences[i : i + self._batch_size]
            batch_embs = np.asarray(self.embedding_function(batch), dtype=np.float32)
            embs.append(batch_embs)
        E = np.vstack(embs)
        return self._l2_normalize(E)

    def _get_similarity_matrix(self, sentences: List[str]) -> np.ndarray:
        """Calcula similitud coseno E @ E.T. Opcionalmente atenúa fuera de banda."""
        E = self._batched_embeddings(sentences)
        M = E @ E.T  # coseno al estar L2-normalizado

        # Centrado + escalado sobre off-diagonales para estabilizar DP
        n = M.shape[0]
        if n >= 2:
            tri = M[np.triu_indices(n, k=1)]
            mu, sigma = float(tri.mean()), float(tri.std() + 1e-12)
            M = (M - mu) / sigma
        np.fill_diagonal(M, 0.0)  # la diagonal no debe influir

        if self._band is not None and self._band >= 0:
            # Atenúa fuera de la banda para favorecer coherencia local
            for i in range(n):
                lo = max(0, i - self._band)
                hi = min(n, i + self._band + 1)
                if lo > 0:
                    M[i, :lo] *= 0.0
                if hi < n:
                    M[i, hi:] *= 0.0
        return M

    @staticmethod
    def _prefix_sums_2d(A: np.ndarray) -> np.ndarray:
        return A.cumsum(0).cumsum(1)

    @staticmethod
    def _sum_submatrix(pref: np.ndarray, i: int, j: int) -> float:
        """Suma de A[i:j+1, i:j+1] usando prefijos 2D."""
        a = pref[j, j]
        b = pref[i - 1, j] if i > 0 else 0.0
        c = pref[j, i - 1] if i > 0 else 0.0
        d = pref[i - 1, i - 1] if i > 0 else 0.0
        return float(a - b - c + d)

    def _max_cluster_size_guess(self, sentences: List[str]) -> int:
        # Estima cuántos "pre-chunks" caben en un chunk final
        approx = max(1, self._chunk_size // max(1, self._min_chunk_size))
        # Cota superior razonable para evitar intentar bloques enormes
        return int(min(64, max(1, approx)))

    def _optimal_segmentation(
        self, matrix: np.ndarray, max_cluster_size: int
    ) -> List[Tuple[int, int]]:
        """DP que maximiza la suma intra-cluster menos penalización por cluster.
        Devuelve pares (start, end) inclusivos.
        """
        n = matrix.shape[0]
        if n == 0:
            return []

        pref = self._prefix_sums_2d(matrix)
        dp = np.full(n, -np.inf, dtype=np.float64)
        start_idx = np.zeros(n, dtype=int)

        for i in range(n):
            best_v = -np.inf
            best_s = 0
            max_s = min(max_cluster_size, i + 1)
            for s in range(1, max_s + 1):
                j = i - s + 1
                reward = self._sum_submatrix(pref, j, i) - self._lambda
                if j > 0:
                    reward += dp[j - 1]
                if reward > best_v:
                    best_v, best_s = reward, j
            dp[i] = best_v
            start_idx[i] = best_s

        clusters: List[Tuple[int, int]] = []
        k = n - 1
        while k >= 0:
            j = start_idx[k]
            clusters.append((j, k))
            k = j - 1
        clusters.reverse()
        return clusters

    # ------------------------------ API -----------------------------------
    def split_text(self, text: str) -> List[str]:
        # 1) Pre-chunks por tokens
        sentences = self.splitter.split_text(text)
        if not sentences:
            return []

        # Protección para textos enormes: aumenta min_chunk_size de forma adaptativa
        # hasta que el número de pre-chunks sea manejable
        MAX_PRECHUNKS = 2000
        if len(sentences) > MAX_PRECHUNKS:
            # Re-splitter más grueso
            min_size = self._min_chunk_size
            while len(sentences) > MAX_PRECHUNKS and min_size < self._chunk_size:
                min_size = min(self._chunk_size, max(min_size * 2, min_size + 1))
                tmp_splitter = RecursiveTokenChunker(
                    chunk_size=min_size,
                    chunk_overlap=0,
                    length_function=self._length_function,
                    separators=["\n\n", "\n", ".", "?", "!", " ", ""],
                )
                sentences = tmp_splitter.split_text(text)

        # 2) Similitud
        sim = self._get_similarity_matrix(sentences)

        # 3) DP para cortes
        max_cluster = self._max_cluster_size_guess(sentences)
        clusters = self._optimal_segmentation(sim, max_cluster_size=max_cluster)

        # 4) Reconstrucción respetando max_chunk_size por tokens reales
        docs: List[str] = []
        acc: List[str] = []
        acc_tokens = 0

        def flush():
            nonlocal acc, acc_tokens
            if acc:
                docs.append("".join(acc))
                acc, acc_tokens = [], 0

        for start, end in clusters:
            piece = "".join(sentences[start : end + 1])
            t = self._length_function(piece)
            if acc_tokens + t <= self._chunk_size:
                acc.append(piece)
                acc_tokens += t
            else:
                flush()
                if t <= self._chunk_size:
                    acc.append(piece)
                    acc_tokens = t
                else:
                    # Fragmenta internamente si todavía excede el límite
                    # (raro, pero posible cuando el cluster final es grande)
                    tmp_splitter = RecursiveTokenChunker(
                        chunk_size=self._chunk_size,
                        chunk_overlap=0,
                        length_function=self._length_function,
                        separators=["\n\n", "\n", ".", "?", "!", " ", ""],
                    )
                    for sub in tmp_splitter.split_text(piece):
                        if self._length_function(sub) > 0:
                            docs.append(sub)
        flush()
        return docs

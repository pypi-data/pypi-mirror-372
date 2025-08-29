from enum import Enum
from rapidfuzz import fuzz, process
import os
from chromadb.utils import embedding_functions
import tiktoken
from sentence_transformers import SentenceTransformer
import re

def get_openai_embedding_function():
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if openai_api_key is None:
        raise ValueError("You need to set an embedding function or set an OPENAI_API_KEY environment variable.")
    embedding_function = embedding_functions.OpenAIEmbeddingFunction(
        api_key=os.getenv('OPENAI_API_KEY'),
        model_name="text-embedding-3-large"
    )
    return embedding_function

def get_embedding_function(
    model_name: str = "BAAI/bge-m3",
    device: str | None = None,
    normalize_embeddings: bool = True,
):
    """
    Devuelve una función de embeddings sin API KEY (SentenceTransformer).
    model_name: repositorio HuggingFace (p.ej. BAAI/bge-m3, thenlper/gte-large, intfloat/e5-large-v2)
    device: "cpu" | "cuda" | "cuda:0" (por defecto lee EMBEDDINGS_DEVICE o 'cpu')
    """
    if device is None:
        device = os.getenv("EMBEDDINGS_DEVICE", "cpu")

    return embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=model_name,
        device=device,
        normalize_embeddings=normalize_embeddings,
    )

# Count the number of tokens in each page_content
def openai_token_count(string: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding("cl100k_base")
    num_tokens = len(encoding.encode(string, disallowed_special=()))
    return num_tokens

class Language(str, Enum):
    """Enum of the programming languages."""

    CPP = "cpp"
    GO = "go"
    JAVA = "java"
    KOTLIN = "kotlin"
    JS = "js"
    TS = "ts"
    PHP = "php"
    PROTO = "proto"
    PYTHON = "python"
    RST = "rst"
    RUBY = "ruby"
    RUST = "rust"
    SCALA = "scala"
    SWIFT = "swift"
    MARKDOWN = "markdown"
    LATEX = "latex"
    HTML = "html"
    SOL = "sol"
    CSHARP = "csharp"
    COBOL = "cobol"
    C = "c"
    LUA = "lua"
    PERL = "perl"
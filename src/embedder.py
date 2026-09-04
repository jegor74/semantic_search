from collections.abc import Sequence

import numpy as np
from sentence_transformers import SentenceTransformer


MODEL_NAME = "intfloat/multilingual-e5-small"   # default embedding model
_MODEL: SentenceTransformer | None = None       # lazily loaded model instance


def get_embedding_model() -> SentenceTransformer:
    """
    Loads the embedding model once and reuses it.

    Returns:
    - initialized SentenceTransformer model.
    """

    global _MODEL

    if _MODEL is None:
        _MODEL = SentenceTransformer(MODEL_NAME)   # loading model only once

    return _MODEL


def embed_query(query: str) -> np.ndarray:
    """
    Creates a normalized embedding for a search query.

    Args:
    - query: user's search query.

    Returns:
    - normalized one-dimensional query embedding.
    """

    query = query.strip()                           # removing surrounding spaces

    if not query:
        raise ValueError("Query must not be empty.")

    model = get_embedding_model()                  # getting cached model instance
    prepared_query = f"query: {query}"             # adding required E5 prefix

    embedding = model.encode(
        prepared_query,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    return embedding


def embed_passages(
    passages: Sequence[str],
    batch_size: int = 32
) -> np.ndarray:
    """
    Creates normalized embeddings for document passages.

    Args:
    - passages: document chunks.
    - batch_size: number of passages processed simultaneously.

    Returns:
    - matrix of normalized passage embeddings.
    """

    if not passages:
        raise ValueError("Passages must not be empty.")

    cleaned_passages = [
        passage.strip() for passage in passages     # removing surrounding spaces
    ]

    if any(not passage for passage in cleaned_passages):
        raise ValueError("Passages must not contain empty strings.")

    model = get_embedding_model()                   # getting cached model instance

    prepared_passages = [
        f"passage: {passage}"                       # adding required E5 prefix
        for passage in cleaned_passages
    ]

    embeddings = model.encode(
        prepared_passages,
        batch_size=batch_size,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=True
    )

    return embeddings

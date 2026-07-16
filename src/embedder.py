from sentence_transformers import SentenceTransformer
import numpy as np

_MODEL = None


def get_embedding_model() -> SentenceTransformer:                       # making a lazy-loading of model (singleton)
    """
    Loads embedding model for using it later.

    Returns:
    - embedding model
    """

    global _MODEL

    if _MODEL is None:
        _MODEL = SentenceTransformer("intfloat/multilingual-e5-small")  # loading multilingual model (for russian and english books)
        # print(_MODEL.get_embedding_dimension())                       # checking embeddings' dimension (384)

    return _MODEL


def embed_single(text: str) -> np.ndarray:
    """
    Uses embedding model and makes embedding from text.

    Args:
    - text: a string of raw text

    Returns:
    - text's embedding with dimension = 384 
    """
    
    model = get_embedding_model()                                       # loading model

    return model.encode([text], convert_to_numpy=True)[0]               # returning embedding



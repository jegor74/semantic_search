from sentence_transformers import SentenceTransformer
from pathlib import Path
import numpy as np
import faiss

def create_index(embeddings: np.ndarray, metric: str = "cosine") -> faiss.Index:
    """
    Creates index of embeddings using metric.

    Args:
    - embeddings: np.ndarray of embeddings (matrix)
    - metric: defines the distance metric: 'cosine' for cosine similarity or 'l2' for Euclidean distance.

    Returns:
    - index: FAISS index of embeddings
    """

    dim = embeddings.shape[1]            # embeddings' dimension

    if metric == "cosine":               # if distance calculate with cosine distance
        faiss.normalize_L2(embeddings)   # normalizing embeddings for cosine distance
        index = faiss.IndexFlatIP(dim)   # creating index for cosine similarity (Inner Product)
    elif metric == "l2":
        index = faiss.IndexFlatL2(dim)   # creating index for Euclidean distance
    else:
        raise ValueError("Choosing metric not found. Choose 'cosine' or 'l2")

    index.add(embeddings)                # adding embeddings to index

    return index                         # returns maded index


def save_index(index: faiss.Index, index_path: str = "data/embeddings/faiss.index") -> None:
    """
    Saves FAISS index to disk.

    Args:
    - index: FAISS index of embeddings
    - index_path: path for saving indexes
    """
    
    path = Path(index_path)                           # making path to directory

    path.parent.mkdir(parents=True, exist_ok=True)    # making directory if it not exists
    faiss.write_index(index, index_path)              # writing index to the directory

    print(f"✅ Saved: {path}")                        # message

 
def load_index(index_path: str = "data/embeddings/faiss.index") -> faiss.Index:
    """
    Load saved FAISS index from disk and returns it.

    Args:
    - index_path: path of saved index

    Returns:
    - index: FAISS index of embedding
    """
    
    path = Path(index_path)               # making path of index
    
    if not path.exists():                 # if file faiss.index not exists
        raise FileNotFoundError("File faiss.index not found. Try to create it.")

    return faiss.read_index(index_path)   # FAISS index
    

def search(query_vector: np.ndarray, index: faiss.Index, k: int = 5, normalize: bool = True) -> tuple:
    """
    Searchs the nearest chunks by query vector.

    Args:
    - query_vector: numpy array - embedding of query
    - index: loaded FAISS index of query
    - k: count of results (default = 5)
    - normalize: whether to normalize the query vector (required for cosine similarity with IndexFlatIP)
    """
    
    if query_vector.shape[0] != index.d:
        raise ValueError("The dimensions of query_vector and index are not the same.")

    query = query_vector.reshape(1, -1)          # making query_vector to (1, dim) form
    
    if normalize:
        faiss.normalize_L2(query)                # normalizing query vector

    distances, indices = index.search(query, k)  # searching top-k nearest chunks and saving their distances and indecies

    return distances, indices

import sys
import json
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from pydantic import BaseModel
from pathlib import Path
from typing import AsyncGenerator, Dict, List, Union

sys.path.append(str(Path(__file__).parent.parent))       # adding root of project to the path

from src.embedder import embed_query
from src.indexer import load_index, search


index = None                                             # global variable for loading index
chunks = None                                            # global variable for loading chunks


class SearchRequest(BaseModel):
    query: str
    top_k: int = 3

class SearchResponse(BaseModel):
    results: List[Dict[str, Union[str, float]]]


@asynccontextmanager
async def load_models(_app: FastAPI) -> AsyncGenerator:  # the "app" variable is not using
    """
    Loads index and chunks at the start of the server.
    """

    global index, chunks
    index = load_index()
    with open("data/metadata/chunks.json", "r", encoding="utf-8") as f:
        chunks = json.load(f)
    print("✅ Index and chunks loaded")

    yield


app = FastAPI(title="Semantic Search API", lifespan=load_models)             # FastAPI initialization


@app.post("/search", response_model=SearchResponse)
async def search_endpoint(request: SearchRequest) -> SearchResponse:
    """
    Takes request and returns top-k relevant chunks.

    Args:
    - request: user's question

    Returns:
    - chunks
    """

    if index is None or chunks is None:
        raise HTTPException(status_code=503, detail="The model is not load")
    
    query_vector = embed_query(request.query)                             # generating embedding of request
    distances, indices = search(query_vector, index, k=request.top_k)     # searching in index
    
    results = []                                                          # answer forming
    for i, idx in enumerate(indices[0]):
        chunk_data = chunks[idx]
        results.append({
            "text": chunk_data["text"],
            "source": chunk_data["source"],
            "distance": float(distances[0][i])
        })
    
    return SearchResponse(results=results)


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Checks performanse.
    """

    return {"status": "ok"}


@app.get("/")
def root():
    return {"message": "Semantic Search API is running"}

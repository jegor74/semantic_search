import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))     # adds project's root directory to Python seatching path

from src.data_loader import load_text_files, save_parsed_documents
from src.chunker import chunk_documents, save_chunks_to_file
from src.embedder import embed_single
from src.indexer import create_index, save_index
import numpy as np


files = load_text_files()
save_parsed_documents(files)
print("✅ Files loaded, cleaned and saved.")

chunks = chunk_documents(files)
save_chunks_to_file(chunks)
print("✅ Chunks maded and saved.")

embeddings_list = []
for chunk in chunks:
    vector = embed_single(chunk["text"])
    embeddings_list.append(vector)
embeddings = np.array(embeddings_list)
print("✅ Embeddings created.")

index = create_index(embeddings)
save_index(index)
print("✅ Indexes created and saved.")

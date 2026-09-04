import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))     # adds project's root directory to Python seatching path

from src.data_loader import clean_documents, load_pdf_files, load_text_files, save_parsed_documents
from src.chunker import chunk_documents, save_chunks_to_file
from src.embedder import embed_passages
from src.indexer import create_index, save_index


raw_documents = {}                                             # storing loaded source documents
raw_documents.update(load_text_files())
raw_documents.update(load_pdf_files())

documents = clean_documents(raw_documents)                     # cleaning documents in memory

if not documents:
    raise RuntimeError(
        "No valid documents were loaded from the data/raw directory."
    )

save_parsed_documents(documents)
print("✅ Documents loaded, cleaned and saved.")


chunks = chunk_documents(documents)
save_chunks_to_file(chunks)
print("✅ Chunks maded and saved.")

if not chunks:
    raise RuntimeError(
        "No chunks were created. Check the data/raw directory."
    )

chunk_texts = [
    chunk["text"] for chunk in chunks              # collecting texts for encoding
]

embeddings = embed_passages(
    chunk_texts,
    batch_size=32                                  # encoding passages in batches
)

print(
    f"✅ Created {len(embeddings)} embeddings "
    f"with dimension {embeddings.shape[1]}."
)

index = create_index(embeddings)
save_index(index)
print("✅ Indexes created and saved.")

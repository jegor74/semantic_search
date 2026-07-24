import json
import nltk
from typing import List, Dict, Any


nltk.download("punkt_tab")


def split_text_by_tokens(text: str, chunk_size: int = 200, overlap: int = 50, separator: str = " ") -> List[str]:
    """
    Splits text into chunks of chunk_size words with overlap.

    Args:
    - text: raw text
    - chunk_size: number of words in each chunk (default = 200)
    - overlap: overlap in words between adjacent chunks (default = 50)
    - separator: default separator (space) for splitting words

    Returns:
    - list of chunks (words)
    """

    words = text.split(separator)                  # splitting text -> List[str]
    chunks = []                                    # list of chunks (words)
    step = chunk_size - overlap                    # default = 150

    for i in range(0, len(words), step):           # iterate over words in step = 150
        chunk_words = words[i:i+chunk_size]        # creating a chunk from a slice of words
        chunk_text = separator.join(chunk_words)   # joining the chunk's words back into a single string
        chunks.append(chunk_text)                  # appending chunk to list

        if i + chunk_size >= len(words):           # if remaining words are fewer than step, exit the loop
            break

    return chunks


def split_text_by_sentences(text: str, chunk_size: int = 200, overlap: int = 50) -> List[str]:
    """
    Splits text into chunks by sentences, trying to reach chunk_size words.
    Overlap is applied at the sentence level.

    Args:
    - text: raw text
    - chunk_size: number of words in each chunk (default = 200)
    - overlap: overlap in words between adjacent chunks (default = 50)

    Returns:
    - list of text chunks (each chunk is a string)
    """

    sentences = nltk.sent_tokenize(text)                          # splitting text by sentences

    if not sentences:                                             # if text is empty return empty array
        return []

    chunks = []
    current_chunk = []
    current_word_count = 0

    for sent in sentences:                                        # groupping sentences to chunks
        sent_word_count = len(sent.split())

        if current_word_count + sent_word_count <= chunk_size:    # appending sentence if current chunk + new sentence <= chunk_size
            current_chunk.append(sent)
            current_word_count += sent_word_count
        else:
            if current_chunk:                                     # saving current chunk if it's not empty
                chunks.append(" ".join(current_chunk))

            overlap_words = 0                                     # starting new chunk with overlap
            overlap_sentences = []                                # taking last sentences from previous chunk for making overlap

            for prev_sent in reversed(current_chunk):             # going from the end of current chunk and assemly sentence while not gaining overlap
                prev_word_count = len(prev_sent.split())

                if overlap_words + prev_word_count <= overlap:    # inserting previous sentence if overlap words + previous sentence <= overlap
                    overlap_sentences.insert(0, prev_sent)
                    overlap_words += prev_word_count
                else:
                    break                                         # stop adding sentences once overlap limit is reached

            current_chunk = overlap_sentences + [sent]            # new chunk starts from overlap sentences + current sentence
            current_word_count = overlap_words + sent_word_count


    if current_chunk:                                             # appending last chunk if it's not empty
        chunks.append(" ".join(current_chunk))


    return chunks


def chunk_documents(documents: Dict[str, str], chunk_size: int = 200, overlap: int = 50) -> List[Dict[str, Any]]:
    """
    Converts a {filename: text} dictionary into a list of chunks with metadata.

    Args:
    - documents: dictionary {filename: text}
    - chunk_size: number of words in each chunk (default = 200)
    - overlap: overlap in words between adjacent chunks (default = 50)
    
    Returns:
    - list of dictionaries:
        {
            "text": "text of the chunk",
            "source": "filename",
            "chunk_id": 0,
            "char_start": 0, 
            "char_end": 150
        }
    """
    
    all_chunks = []                                                          # list of dictionaries

    for filename, text in documents.items():                                 # iterate over the documents
        chunks = split_text_by_sentences(text, chunk_size, overlap)          # splitting the text into chunks 
        
        for idx, chunk_text in enumerate(chunks):                            # iterate over chunks with enumeration
            all_chunks.append({                                              # appending a dictionary with chunk metadata to the list
                "text": chunk_text,
                "source": filename, 
                "chunk_id": idx,
                "char_start": idx * (chunk_size - overlap) * 5,              # approximate
                "char_end": (idx * (chunk_size - overlap) + chunk_size) * 5  # approximate
                })
    
    return all_chunks


def save_chunks_to_file(chunks: List[Dict[str, Any]], output_file: str = "data/metadata/chunks.json") -> None:
    """
    Saves a list of chunks to a JSON file for later use.
    """
    
    with open(output_file, "w", encoding="utf-8") as file:      # opens file to write
        json.dump(chunks, file, ensure_ascii=False, indent=2) 
        # json.dump writes the chunks list ti a file in JSON format
        # ensure_ascii=False keeps Unicode characters (e.g., Russian) readable
        # indent=2 adds pretty-printing with 2 spaces per level

    print(f"✅ Saved: {len(chunks)} chunks to {output_file}")   # message

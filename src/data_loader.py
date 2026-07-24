from pathlib import Path
import re
import pymupdf


def load_text_files(raw_dir: str = "data/raw") -> dict:
    """
    Loads all .txt files from raw_dir directory.
    Returns dictionary {file_name: text}.
    """

    documents = {}                 # dictionary
    raw_path = Path(raw_dir)       # path with all .txt files for loading

    if not raw_path.exists():
        raise FileNotFoundError(f"Directory {raw_dir} not found. Make it and put .txt files there.")

    for file_path in raw_path.glob("*.txt"):                       # reading each file's path and opening it with UTF-8 encoding
        try:
            with open(file_path, "r", encoding="utf-8") as file:   # opening txt file
                text = file.read()                                 # if file can't be opened, raise exception and skip this file
        except Exception as e:
            print(f"⚠️ Skipping {file_path.name}: {e}")
            continue

        documents[file_path.name] = text                           # add file's text to dictionary

    return documents


def load_pdf_files(raw_dir: str = "data/raw") -> dict:
    """
    Loads all .pdf files from raw_dir directory.
    Returns dictionary {file_name: text}.
    """

    documents = {}                 # dictionary
    raw_path = Path(raw_dir)       # path with all .pdf files for loading

    if not raw_path.exists():
        raise FileNotFoundError(f"Directory {raw_dir} not found. Make it and put .pdf files there.")

    for file_path in raw_path.glob("*.pdf"):                       # reading each file's path and opening it with UTF-8 encoding
        try:
            doc = pymupdf.open(file_path)                          # opening .pdf file
        except Exception as e:                                     # if file can't be opened, raise exception and skip this file
            print(f"⚠️ Skipping {file_path.name}: {e}")
            continue

        texts = []                                                 # empty array for text from .pdf file
        for page in doc:                                           # getting text of .pdf file from each page
            page_text = page.get_text()
            if page_text != "":                                    # if page is empty, skip this page
                texts.append(page_text) 
        
        text = "".join(texts)                                      # making text string from array
        documents[file_path.name] = text                           # add file's text to dictionary
        
    documents = {k: v for k, v in documents.items() if v.strip()}  # removing empty documents from dictionary
    return documents


def clean_text(text: str) -> str:
    """
    Cleans text: removes extra spaces, special characters, fixes line breaks.

    Args:
    - text: raw text

    Returns:
    - cleaned text
    """
    
    text = re.sub(r"(\w+)-\s*(\w+)", r"\1\2", text)      # removing soft hyphens and line breaks from PDF
    text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)         # removing lonely \n (inside paragraphs)
    text = re.sub(r"[^\w\s.,!?()%+*/@=#&-]", "", text)   # removing disallowed characters, keeping only safe punctuation and math symbols
    text = re.sub(r"\s+", " ", text)                     # removing multiple spaces (\s, \t) and line breaks(\n)
    text = re.sub(r"\s+([.,!?;:])", r"\1", text)         # removing space before punctuation


    return text.strip()                                  # returning cleaned text without spaces at start and end of the string


def save_parsed_documents(documents: dict, parsed_dir: str = "data/parsed") -> None:
    """
    Saves cleaned texts to the parsed_dir directory with the same file name.
    """

    parsed_path = Path(parsed_dir)
    parsed_path.mkdir(parents=True, exist_ok=True)                # making directory with all intermediate directories, if they're not exist.

    for filename, text in documents.items():                      # reading every file in dictionary
        clean = clean_text(text)                                  # cleaning file's text
        output_path = parsed_path / filename                      # making path to new file
        
        with open(output_path, "w", encoding="utf-8") as file:    # opens file and writes cleaned text
            file.write(clean)

        print(f"✅ Saved: {output_path}")                         # message

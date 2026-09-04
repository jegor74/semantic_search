import re
import pymupdf
import pymupdf4llm
from pathlib import Path


def load_text_files(raw_dir: str = "data/raw") -> dict:
    """
    Loads all .txt files from raw_dir directory.

    Returns:
    - dictionary {file_name: text}.
    """

    documents = {}                 # dictionary
    raw_path = Path(raw_dir)       # path with all .txt files for loading

    if not raw_path.exists():
        raise FileNotFoundError(f"Directory {raw_dir} not found. Make it and put .txt files there.")

    for file_path in raw_path.glob("*.txt"):                       # reading each file's path and opening it with UTF-8 encoding
        print(f"⏳ Processing (.txt): {file_path.name}")
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

    Returns:
    - dictionary {file_name: text}.
    """

    documents = {}                 # dictionary
    raw_path = Path(raw_dir)       # path with all .pdf files for loading

    if not raw_path.exists():
        raise FileNotFoundError(f"Directory {raw_dir} not found. Make it and put .pdf files there.")

    for file_path in raw_path.glob("*.pdf"):                       # reading each file's path and opening it with UTF-8 encoding
        print(f"⏳ Processing (.pdf): {file_path.name}")
        try:
            md_data = pymupdf4llm.to_markdown(file_path)           # making .md file from .pdf
            
            if isinstance(md_data, list):                          # taking text from list of dicts
                text = "\n".join([item.get("text", "") for item in md_data if "text" in item])
            else:
                text = str(md_data)

        except Exception as e:                                     # if file can't be opened, raise exception and skip this file
            print(f"⚠️ Skipping {file_path.name}: {e}")
            continue
        
        if text.strip():
            documents[file_path.name] = text

    documents = {k: v for k, v in documents.items() if v.strip()}  # removing empty documents from dictionary
    return documents


def load_pdf_files_old(raw_dir: str = "data/raw") -> dict:
    """
    Loads all .pdf files from raw_dir directory.

    Returns:
    - dictionary {file_name: text}.
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
    Cleans extracted text while preserving paragraph structure.

    Args:
    - text: raw extracted text.

    Returns:
    - cleaned text.
    """

    text = text.replace("\r\n", "\n")                         # normalizing Windows line breaks
    text = text.replace("\r", "\n")                           # normalizing old-style line breaks
    text = text.replace("\xa0", " ")                          # replacing non-breaking spaces
    text = text.replace("\u00ad", "")                         # removing soft hyphens
    text = text.replace("\u200b", "")                         # removing zero-width spaces

    text = re.sub(
        r"<!--.*?-->",
        " ",
        text,
        flags=re.DOTALL                                      # removing multiline HTML comments
    )
    text = re.sub(
        r"<br\s*/?>",
        " ",
        text,
        flags=re.IGNORECASE                                  # replacing HTML line breaks
    )
    text = re.sub(r"<[^>]+>", " ", text)                     # removing remaining HTML tags

    text = re.sub(
        r"(?<=\w)-[ \t]*\n[ \t]*(?=\w)",
        "",
        text                                                 # joining words broken across lines
    )

    text = re.sub(
        r"(?<!\n)\n(?!\n)",
        " ",
        text                                                 # replacing single line breaks
    )
    text = re.sub(r"[ \t]+", " ", text)                      # removing repeated horizontal spaces
    text = re.sub(r" *\n{2,} *", "\n\n", text)               # preserving paragraph boundaries
    text = re.sub(r" +([.,!?;:])", r"\1", text)              # removing spaces before punctuation
    text = re.sub(r"-{4,}", "", text)                        # removing long hyphen sequences

    return text.strip()


def clean_documents(documents: dict[str, str]) -> dict[str, str]:
    """
    Cleans loaded documents and removes empty results.

    Args:
    - documents: dictionary containing filenames and raw texts.

    Returns:
    - dictionary containing filenames and cleaned texts.
    """

    cleaned_documents = {}

    for filename, text in documents.items():
        cleaned_text = clean_text(text)                       # cleaning current document

        if not cleaned_text:
            print(f"⚠️ Skipping empty document: {filename}")
            continue

        cleaned_documents[filename] = cleaned_text             # saving cleaned document in memory

    return cleaned_documents


def save_parsed_documents(documents: dict[str, str], parsed_dir: str = "data/parsed") -> None:
    """
    Saves cleaned documents to the parsed directory.

    Args:
    - documents: dictionary containing filenames and cleaned texts.
    - parsed_dir: directory for processed documents.
    """

    parsed_path = Path(parsed_dir)
    parsed_path.mkdir(
        parents=True,
        exist_ok=True                                          # creating output directory
    )

    for filename, text in documents.items():
        source_path = Path(filename)                           # getting original filename

        if source_path.suffix.lower() == ".pdf":
            output_name = f"{source_path.stem}.md"             # saving parsed PDF as Markdown
        else:
            output_name = source_path.name                     # preserving text filename

        output_path = parsed_path / output_name

        with open(output_path, "w", encoding="utf-8") as file:
            file.write(text)                                   # writing already cleaned text

        print(f"✅ Saved: {output_path}")

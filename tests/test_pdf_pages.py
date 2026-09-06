import json
from unittest.mock import patch
from src.data_loader import clean_pages, load_pdf_pages, save_parsed_pages


def test_load_pdf_pages_preserves_source_page_numbers(tmp_path):
    """
    Preserves original page numbers, including empty pages.
    """

    pdf_path = tmp_path / "sample.pdf"
    pdf_path.touch()                                   # creating a placeholder input file

    extracted_pages = [
        {"metadata": {"page_number": 1}, "text": "First page."},
        {"metadata": {"page_number": 3}, "text": ""}
    ]

    with patch(
        "src.data_loader.pymupdf4llm.to_markdown",
        return_value=extracted_pages
    ) as extract:
        records = load_pdf_pages(pdf_path, pages=[0, 2])

    extract.assert_called_once_with(
        str(pdf_path),
        pages=[0, 2],
        page_chunks=True
    )

    assert records == [
        {"source": "sample.pdf", "page": 1, "text": "First page."},
        {"source": "sample.pdf", "page": 3, "text": ""}
    ]


def test_clean_pages_preserves_metadata_and_input():
    """
    Cleans text without changing metadata or original records.
    """

    raw_text = "машин-\nное <br> обучение"
    pages = [
        {
            "source": "sample.pdf",
            "page": 3,
            "text": raw_text
        }
    ]

    cleaned = clean_pages(pages)

    assert cleaned == [
        {
            "source": "sample.pdf",
            "page": 3,
            "text": "машинное обучение"
        }
    ]
    assert pages[0]["text"] == raw_text                 # checking input preservation


def test_clean_pages_skips_empty_pages_without_renumbering():
    """
    Removes empty pages while keeping original PDF page numbers.
    """

    pages = [
        {"source": "sample.pdf", "page": 1, "text": "First page."},
        {"source": "sample.pdf", "page": 2, "text": " \n\t "},
        {"source": "sample.pdf", "page": 3, "text": "Third page."}
    ]

    cleaned = clean_pages(pages)

    assert [page["page"] for page in cleaned] == [1, 3]


def test_save_parsed_pages_preserves_records(tmp_path):
    """
    Creates parent directories and preserves records in JSON.
    """

    pages = [
        {"source": "sample.pdf", "page": 3, "text": "Машинное обучение."}
    ]
    output_path = tmp_path / "parsed" / "pages.json"

    save_parsed_pages(pages, output_path)

    with output_path.open("r", encoding="utf-8") as file:
        restored_pages = json.load(file)               # loading saved records

    assert restored_pages == pages

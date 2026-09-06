from unittest.mock import patch
from src.data_loader import load_pdf_pages


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

from src.chunker import chunk_pages
from unittest.mock import patch


def test_chunk_pages_preserves_metadata():
    """
    Preserves chunk metadata and numbering while skipping empty pages.
    """

    pages = [
        {"source": "sample.pdf", "page": 1, "text": "First page."},
        {"source": "sample.pdf", "page": 2, "text": " \n\t "},
        {"source": "sample.pdf", "page": 3, "text": "Third page."}
    ]

    side_effect = [
        ["First fragment.", "Second fragment.", "Third fragment."],
        ["Fourth fragment.", "Fifth fragment."]
    ]
    
    with patch("src.chunker.split_text_by_sentences", side_effect=side_effect):
        result = chunk_pages(pages, 200, 50)

    assert len(result) == 5
    assert [record["page"] for record in result] == [1, 1, 1, 3, 3]

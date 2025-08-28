from unittest.mock import MagicMock

from chATLAS_Chains.utils.doc_utils import combine_documents
from chATLAS_Embed import Document


def test_combine_documents_returns_string():
    # Arrange: Create mock Document objects
    mock1 = MagicMock(spec=Document)
    mock1.page_content = "Hello."
    mock1.metadata = {
        "last_modification": "2025-04-08",  # Add mock metadata
        "name": "Document 1",
    }

    mock2 = MagicMock(spec=Document)
    mock2.page_content = "Hola."
    mock2.metadata = {
        "last_modification": "2025-04-08",  # Add mock metadata
        "name": "Document 2",
    }

    # Act: Combine documents
    result = combine_documents([mock1, mock2])

    # Assert: Check that result is a string
    assert isinstance(result, str), "combine_documents should return a string"

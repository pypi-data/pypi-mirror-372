"""
Unit tests for search_runnable

**NOTE** These require a running postgres database with a populated vector store.

The fixtures used for the tests are defined in conftest.py and are automatically gathered by pytest

"""

import pytest
from langchain_core.runnables import RunnableSequence
from pydantic import ValidationError

from chATLAS_Chains.search.basic import search_runnable


def test_search_runnable_returns_runnablesequence(twiki_vectorstore):
    """
    Test the search_runnable function with a populated vector store.
    """
    print(type(twiki_vectorstore))
    # Create a runnable for searching
    searcher = search_runnable(vectorstore=twiki_vectorstore)

    assert isinstance(searcher, RunnableSequence)


def test_search_runnable_returns_runnablesequence_with_list_of_vectorstores(three_vectorstores):
    runnable = search_runnable(three_vectorstores)
    assert isinstance(runnable, RunnableSequence)


def test_search_runnable_error_on_invalid_input():
    with pytest.raises(ValidationError):
        search_runnable("not_a_vectorstore")  # type: ignore[arg-type]


def test_search_runnable_returns_docs_and_questions(twiki_vectorstore):
    searcher = search_runnable(vectorstore=twiki_vectorstore)
    output = searcher.invoke("What is the Higgs boson?")

    assert "docs" in output
    assert "question" in output


def test_search_runnable_multiple_vectorstores(three_vectorstores):
    searcher = search_runnable(vectorstore=three_vectorstores)
    output = searcher.invoke("What is the Higgs boson?")

    assert "docs" in output
    assert "question" in output

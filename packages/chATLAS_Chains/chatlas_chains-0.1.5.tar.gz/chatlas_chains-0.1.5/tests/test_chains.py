"""
Unit tests for basic_retrieval_chain

These**NOTE** These require a running postgres database with a populated vector store.

The fixtures used for the tests are defined in conftest.py and are automatically gathered by pytest
"""

import pytest
from langchain_core.documents import Document
from langchain_core.runnables import RunnableSequence
from pydantic import ValidationError

from chATLAS_Chains.chains.advanced import advanced_rag
from chATLAS_Chains.chains.basic import basic_retrieval_chain
from chATLAS_Chains.llm.groq import RetryConfig
from chATLAS_Chains.llm.model_selection import GROQ_PRODUCTION_MODELS
from chATLAS_Chains.prompt.starters import CHAT_PROMPT_TEMPLATE
from chATLAS_Chains.vectorstore import get_vectorstore


@pytest.fixture
def retry_config():
    """Retry config to use in tests"""
    return RetryConfig(max_retries=2, max_delay=120.0)


def test_basic_retrieval_chain_returns_runnablesequence(twiki_vectorstore):
    chain = basic_retrieval_chain(prompt=CHAT_PROMPT_TEMPLATE, vectorstore=twiki_vectorstore, model_name="gpt-4o-mini")

    assert isinstance(chain, RunnableSequence)


def test_search_runnable_returns_runnablesequence_with_list_of_vectorstores(three_vectorstores):
    chain = basic_retrieval_chain(prompt=CHAT_PROMPT_TEMPLATE, vectorstore=three_vectorstores, model_name="gpt-4o-mini")

    assert isinstance(chain, RunnableSequence)


def test_search_runnable_error_on_invalid_input():
    with pytest.raises(ValidationError):
        basic_retrieval_chain(
            prompt=CHAT_PROMPT_TEMPLATE,
            vectorstore="not a vectorstore",  # type: ignore[arg-type]
            model_name="gpt-4o-mini",
        )


def test_basic_retrieval_chain_returns_docs_and_answer(twiki_vectorstore, retry_config):
    chain = basic_retrieval_chain(
        prompt=CHAT_PROMPT_TEMPLATE,
        vectorstore=twiki_vectorstore,
        model_name=GROQ_PRODUCTION_MODELS[0],
        retry_config=retry_config,
    )
    output = chain.invoke("What is the Higgs boson?")

    assert "docs" in output
    assert "answer" in output

    assert isinstance(output["docs"], list)


def test_basic_retrieval_chain_multiple_vectorstores(three_vectorstores, retry_config):
    chain = basic_retrieval_chain(
        prompt=CHAT_PROMPT_TEMPLATE,
        vectorstore=three_vectorstores,
        model_name=GROQ_PRODUCTION_MODELS[0],
        retry_config=retry_config,
    )
    output = chain.invoke("What is the Higgs boson?")

    assert "docs" in output
    assert "answer" in output

    assert isinstance(output["docs"], list)

    sources = set([doc.metadata.get("source") for doc in output["docs"]])
    expected_sources = {"twiki", "MkDocs", "CDS"}
    assert sources == expected_sources, (
        f"Unexpected sources from three vectorstore search: {sources}, expected {expected_sources}"
    )


def test_advanced_rag_chain(twiki_vectorstore, retry_config):
    # TODO: this is required currently requried for search to work
    search_kwargs = {
        "k_text": 3,
        "k": 15,
        "date_filter": "01-01-2010",
        # "type": ["twiki"],
    }

    chain = advanced_rag(
        prompt=CHAT_PROMPT_TEMPLATE,
        vectorstore=twiki_vectorstore,
        model_name=GROQ_PRODUCTION_MODELS[0],
        retry_config=retry_config,
    )
    output = chain.invoke(
        {"question": "What is the Higgs boson?", "search_kwargs": search_kwargs},
    )

    assert "docs" in output
    assert "answer" in output
    assert isinstance(output["docs"], list)
    assert isinstance(output["docs"][0], Document)

    # test with the additional options turned on (besides rerank)
    chain = advanced_rag(
        prompt=CHAT_PROMPT_TEMPLATE,
        vectorstore=twiki_vectorstore,
        model_name=GROQ_PRODUCTION_MODELS[0],
        enable_query_rewriting=True,
        enable_rrf=True,
    )

    output = chain.invoke(
        {"question": "What is the Higgs boson?", "search_kwargs": search_kwargs},
    )

    assert "docs" in output
    assert "answer" in output
    assert isinstance(output["docs"], list)
    assert isinstance(output["docs"][0], Document)


def test_advanced_rag_chain_multiple_vectorstores(three_vectorstores, retry_config):
    search_kwargs = {
        "k_text": 3,
        "k": 15,
        "date_filter": "01-01-2010",
        # "type": ["twiki"],
    }

    chain = advanced_rag(
        prompt=CHAT_PROMPT_TEMPLATE,
        vectorstore=three_vectorstores,
        model_name=GROQ_PRODUCTION_MODELS[0],
        retry_config=retry_config,
    )
    output = chain.invoke(
        {"question": "What is the Higgs boson?", "search_kwargs": search_kwargs},
    )

    assert "docs" in output
    assert "answer" in output
    assert isinstance(output["docs"], list)
    assert isinstance(output["docs"][0], Document)

    sources = set([doc.metadata.get("source") for doc in output["docs"]])
    expected_sources = {"twiki", "MkDocs", "CDS"}
    assert sources == expected_sources, (
        f"Unexpected sources from three vectorstore search: {sources}, expected {expected_sources}"
    )

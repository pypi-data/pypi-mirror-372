import pytest
from langchain_core.documents import Document

from chATLAS_Chains.documents.rrf import reciprocal_rank_fusion, split_docs_by_retriever


@pytest.fixture
def vector_results():
    doc1 = Document(
        page_content="In the Standard Model, the Higgs potential is responsible for electroweak symmetry breaking",
        metadata={"search_type": "vector", "name": "higgs"},
        source="twiki",
        url="",
    )
    doc2 = Document(
        page_content="The top quark is the heaviest known elementary particle",
        # name="top",
        metadata={"search_type": "vector", "name": "top"},
        source="twiki",
        url="",
    )

    return [doc1, doc2]


@pytest.fixture
def text_results():
    doc3 = Document(
        page_content="The gluon is the force carrier of Quantum Chromodynamics (QCD)",
        # name="gluon",
        metadata={"search_type": "text", "name": "gluon"},
        source="twiki",
        url="",
    )
    doc4 = Document(
        page_content="In the Standard Model, the Higgs potential is responsible for electroweak symmetry breaking",
        # name="higgs",
        metadata={"search_type": "text", "name": "higgs"},
        source="twiki",
        url="",
    )
    doc5 = Document(
        page_content="The Large Hadron Collider (LHC) is the world's largest and most powerful particle accelerator",
        # name="lhc",
        metadata={"search_type": "text", "name": "lhc"},
        source="twiki",
        url="",
    )

    return [doc3, doc4, doc5]


@pytest.fixture
def docs_dict(vector_results, text_results):
    return {
        "vector": vector_results,
        "text": text_results,
    }


def test_split_docs_by_retriever(vector_results, text_results):
    # pass it the combined list, it should re-split
    combined = vector_results + text_results

    split = split_docs_by_retriever(combined)

    assert isinstance(split, dict), "return type should be dict"
    assert "text" in split, "missing retriever type in returned dict"
    assert "vector" in split, "missing retriever type in returned dict"
    assert len(split["text"]) == len(text_results), "text results length mismatch"
    assert len(split["vector"]) == len(vector_results), "vector results length mismatch"


def test_split_docs_by_retriever_missing_search_type(vector_results):
    # remove search_type from one doc
    vector_results[0].metadata.pop("search_type")

    with pytest.raises(ValueError, match="search_type metadata field missing from Document.metadata"):
        split_docs_by_retriever(vector_results)


def test_reciprocal_rank_fusion(docs_dict):
    fused = reciprocal_rank_fusion(docs_dict)

    assert isinstance(fused, list), "return type should be list"
    assert len(fused) <= 5, "fused results length exceeds top_k"
    assert all(isinstance(doc, Document) for doc in fused), f"all items in fused results should be {Document} instances"

    assert all("rrf_score" in doc.metadata for doc in fused), "rrf_score missing from Document.metadata"

    # Check that the documents are ordered by score (highest first)
    scores = [doc.metadata["rrf_score"] for doc in fused]
    assert scores == sorted(scores, reverse=True), "documents are not ordered by rrf_score"


def test_reciprocal_rank_fusion_with_docs_splitter(vector_results, text_results):
    """
    Same as above, but check it still works using the actual splitter function
    """
    fused = reciprocal_rank_fusion(split_docs_by_retriever(vector_results + text_results))

    assert isinstance(fused, list), "return type should be list"
    assert len(fused) <= 5, "fused results length exceeds top_k"
    assert all(isinstance(doc, Document) for doc in fused), f"all items in fused results should be {Document} instances"

    assert all("rrf_score" in doc.metadata for doc in fused), "rrf_score missing from Document.metadata"

    # Check that the documents are ordered by score (highest first)
    scores = [doc.metadata["rrf_score"] for doc in fused]
    assert scores == sorted(scores, reverse=True), "documents are not ordered by rrf_score"


def test_reciprocal_rank_fusion_raise_for_negative_k(docs_dict):
    with pytest.raises(ValueError, match="k must be positive"):
        reciprocal_rank_fusion(docs_dict, k=-7)


def test_reciprocal_rank_fusion_raise_for_mismatched_weights(docs_dict):
    weights = {
        "vector": 1.0,
        "text": 1.0,
        "extra": 1.0,
    }

    with pytest.raises(ValueError, match="Weight 'extra' not found in provided results dictionary."):
        reciprocal_rank_fusion(docs_dict, weights=weights)

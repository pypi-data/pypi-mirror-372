"""
Functions for performing Reciprocal Rank Fusion (RRF) on documents retrieved from text and vector search
"""

from langchain_core.documents import Document


def reciprocal_rank_fusion(results: dict, k: float = 60, weights: dict[str, float] | None = None) -> list:
    """
    Fuse search results using weighted Reciprocal Rank Fusion (RRF) algorithm.

    **NOTE** Assumes document lists are already sorted from largest to smallest score.

    Allows adjusting the relative importance of different retrievers
    by applying weights to their RRF contributions.

    :param results: Dictionary containing search results from different retrievers, where each key is the retriever name and value is a list of Documents.
    :param k: RRF constant, controls the influence of rank position
    :param weights: Optional dictionary of weights for each retriever. If the weight is not specified for a retriever, it defaults to 1.0.

    :return: List of Documents sorted by their RRF score, with two new metadata fields:
        - `rrf_score`: The RRF score for each document.
        - `retrievers`: List of retrievers that returned this document.
    """
    rrf_scores = {}
    document_store = {}

    if k < 0:
        raise ValueError("k must be positive")

    if weights is None:
        weights = {}

    for weight_key in weights:
        if weight_key not in results:
            raise ValueError(f"Weight '{weight_key}' not found in provided results dictionary.")

    for key in results:
        if key not in weights:
            weights[key] = 1.0

    if len(results) != len(weights):
        raise ValueError("Number of results and weights are different")

    # Do this for each retriever in the dict
    for retriever, docs in results.items():
        for rank, doc in enumerate(docs, 1):
            id = doc.id

            # initialise score to zero
            if id not in rrf_scores:
                rrf_scores[id] = 0
                document_store[id] = doc

            # weighted score for this retriever
            rrf_scores[id] += weights[retriever] * (1 / (k + rank))

            # track which retrievers had this document
            metadata = document_store[id].metadata
            if "retrievers" not in metadata:
                metadata["retrievers"] = []
            if retriever not in metadata["retrievers"]:
                metadata["retrievers"].append(retriever)

    # Sort and return results
    sorted_results = []
    for id in sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True):
        doc = document_store[id]
        doc.metadata["rrf_score"] = rrf_scores[id]

        sorted_results.append(doc)

    return sorted_results


def split_docs_by_retriever(docs: list[Document]):
    """
    Split a single list of documents using the `search_type` metadata field.

    Returns a dictionary with keys as search types and values as lists of documents.
    """

    retriever_types = []
    for doc in docs:
        if "search_type" not in doc.metadata:
            raise ValueError("search_type metadata field missing from Document.metadata")

        search_type = doc.metadata["search_type"]
        if search_type not in retriever_types:
            retriever_types.append(search_type)

    split_docs = {retriever_type: [] for retriever_type in retriever_types}

    for doc in docs:
        search_type = doc.metadata["search_type"]
        if search_type not in split_docs:
            raise ValueError(f"search_type '{search_type}' not found in split_docs keys")
        split_docs[search_type].append(doc)

    return split_docs


if __name__ == "__main__":
    # Example usage
    from langchain_core.documents import Document

    # Create some example documents
    doc1 = Document(
        page_content="In the Standard Model, the Higgs potential is responsible for electroweak symmetry breaking",
        id="higgs",
        metadata={"search_type": "vector"},
    )
    doc2 = Document(
        page_content="The top quark is the heaviest known elementary particle",
        id="top",
        metadata={"search_type": "vector"},
    )

    vector_results = [doc1, doc2]

    doc3 = Document(
        page_content="The gluon is the force carrier of Quantum Chromodynamics (QCD)",
        id="gluon",
        metadata={"search_type": "text"},
    )
    doc4 = Document(
        page_content="In the Standard Model, the Higgs potential is responsible for electroweak symmetry breaking",
        id="higgs",
        metadata={"search_type": "text"},
    )
    doc5 = Document(
        page_content="The Large Hadron Collider (LHC) is the world's largest and most powerful particle accelerator",
        id="lhc",
        metadata={"search_type": "text"},
    )

    text_results = [doc3, doc4, doc5]

    input_docs = {"text": text_results, "vector": vector_results}

    rrf_results = reciprocal_rank_fusion(input_docs, k=60, weights={"text": 1.0, "vector": 1.5})

    print("RRF Results:")
    for doc in rrf_results:
        print(
            f"Document ID: {doc.id}, RRF Score: {doc.metadata.get('rrf_score', 0)}, Retrievers: {doc.metadata.get('retrievers', [])}"
        )

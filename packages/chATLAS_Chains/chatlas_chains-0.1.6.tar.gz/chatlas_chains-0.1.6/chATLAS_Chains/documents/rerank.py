"""
Uses the Pinecone API to rerank the retrieved documents
"""

import os

from langchain_core.documents import Document
from pinecone import Pinecone


def rerank_documents(
    question: str,
    docs: list[Document],
    reranker_model: str = "cohere-rerank-3.5",
    api_key: str | None = None,
    num_return_docs: int | None = None,
) -> list[Document]:
    """
    Rerank a list of documents using the Pinecone API cross-encoder reranking model.

    Adds the following metadata to each document:
    - `rerank_score`: The score assigned by the reranker model.
    - `rerank_index`: The index of the document in the reranked list.
    - `before_rerank_index`: The original index of the document before reranking.

    :param question: The question to rerank the documents against.
    :type question: str

    :param docs: List of documents to rerank.
    :type docs: list[Document]

    :param reranker_model: The Pinecone model to use for reranking. Defaults to "cohere-rerank-3.5".
    :type reranker_model: str

    :param api_key: Pinecone API key. If not provided, it will look for the PINECONE_API_KEY environment variable.
    :type api_key: str | None

    :param num_return_docs: The number of documents to return after reranking. By default, return all documents
    :type num_return_docs: int | None

    :raises ValueError: If the Pinecone API key is not provided or not set in the environment variable.

    :return: List of documents sorted by rerank score, with updated metadata.
    """
    api_key = api_key or os.getenv("PINECONE_API_KEY")
    if not api_key:
        raise ValueError(
            "Pinecone API key required for reranking. Provide it the api_key argument or set the PINECONE_API_KEY environment variable"
        )
    pc = Pinecone(api_key=api_key)

    if not num_return_docs:
        num_return_docs = len(docs)

    # put documents in the form Pinecone expects
    formatted_docs = [{"text": doc.page_content} for i, doc in enumerate(docs)]

    rerank_scores = pc.inference.rerank(
        model=reranker_model,
        query=question,
        documents=formatted_docs,
        top_n=num_return_docs,
        return_documents=True,
    )

    for reranked_index, item in enumerate(rerank_scores.data):
        original_doc_index = item["index"]

        docs[original_doc_index].metadata["before_rerank_index"] = original_doc_index
        docs[original_doc_index].metadata["rerank_score"] = item["score"]
        docs[original_doc_index].metadata["rerank_index"] = reranked_index

    # Sort the documents by rerank index
    reranked_docs = sorted(docs, key=lambda x: x.metadata.get("rerank_index", float("inf")))

    return reranked_docs


if __name__ == "__main__":
    # Example usage
    question = "What is the significance of the Higgs boson?"
    docs = [
        Document(page_content="Oranges are a fruit"),
        Document(page_content="The top quark is the heaviest known elementary particle"),
        Document(page_content="The Higgs boson is a fundamental particle."),
    ]
    reranked_docs = rerank_documents(question, docs, reranker_model="bge-reranker-v2-m3")

    print("Reranked Documents")

    for doc in reranked_docs:
        print(f"Content: {doc.page_content}")
        print(f"Rerank Score: {doc.metadata.get('rerank_score')}")
        print(f"Rerank Index: {doc.metadata.get('rerank_index')}")
        print(f"Before Rerank Index: {doc.metadata.get('before_rerank_index')}")
        print("-" * 40)

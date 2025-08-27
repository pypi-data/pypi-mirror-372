from langchain_core.runnables import RunnableLambda, RunnableParallel, RunnablePassthrough, RunnableSerializable

from chATLAS_Embed.Base import VectorStore
from chATLAS_Embed.LangChainVectorStore import LangChainVectorStore


def search_runnable(
    vectorstore: VectorStore | list[VectorStore],
) -> RunnableSerializable:
    """
    LangChain RunnableSerializable to search one or more vectorstores in parallel.

    :param vectorstore: A single `VectorStore` or a list of `VectorStore` instances
    :type vectorstore: VectorStore or list[VectorStore]

    :return: A LangChain `RunnableSerializable` that performs retrieval. Results from multiple vectorstores are merged into a single list.
    :rtype: RunnableSerializable
    """

    vectorstores = vectorstore if isinstance(vectorstore, list) else [vectorstore]
    retrievers = [LangChainVectorStore(vector_store=vs) for vs in vectorstores]

    # Create parallel retrieval for each retriever
    retrieved_documents = RunnableParallel(
        {f"docs_{i}": retriever for i, retriever in enumerate(retrievers)} | {"question": RunnablePassthrough()}
    )

    # Merge all retrieved documents into a single list
    def merge_docs(x):
        all_docs = []
        for i in range(len(retrievers)):
            all_docs.extend(x[f"docs_{i}"])
        return all_docs

    # take the retrived docs and merge them, also pass through the question
    processed = RunnableParallel(
        {"docs": RunnableLambda(merge_docs), "question": RunnableLambda(lambda x: x["question"])}
    )

    searcher = retrieved_documents | processed

    return searcher


if __name__ == "__main__":
    # Example usage
    from chATLAS_Chains.vectorstore import get_vectorstore

    cds = get_vectorstore("cds_v1")
    twiki = get_vectorstore("twiki_prod")
    search_chain = search_runnable([cds, twiki])

    # Example input
    question = "What is the Drell-Yan dilepton cross section?"
    result = search_chain.invoke(question)

    print(result)

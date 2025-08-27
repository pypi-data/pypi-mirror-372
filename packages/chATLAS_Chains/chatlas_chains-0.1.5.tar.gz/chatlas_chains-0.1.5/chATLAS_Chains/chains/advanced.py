"""
More advanced RAG workflow with optional query rewriting, reciprocal rank fusion and reranking

Stages:
- (Optional) Query Rewriting - Correct typos and enhance query clarity using LLM
- Retrieval - Retrieve documents using BM25 and vector search
- (Optional) Reciprocal Rank Fusion - Combine results from retrieval modes (e.g. text and vector)
upweighting results that appear in both
- (Optional) Reranking - Rerank documents using Pinecone API cross-encoder model
- Answer Generation - Generate answer using LLM with retrieved context
"""

import argparse
import os
import sys
from typing import TypedDict

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from chATLAS_Chains.documents.rerank import rerank_documents
from chATLAS_Chains.documents.rrf import reciprocal_rank_fusion, split_docs_by_retriever
from chATLAS_Chains.llm.groq import RetryConfig
from chATLAS_Chains.llm.model_selection import GROQ_PRODUCTION_MODELS, get_chat_model
from chATLAS_Chains.prompt.starters import CHAT_PROMPT_TEMPLATE
from chATLAS_Chains.query.query_rewriting import rewrite_query
from chATLAS_Chains.search.basic import search_runnable
from chATLAS_Chains.utils.doc_utils import combine_documents
from chATLAS_Embed.Base import VectorStore


# Define TypedDict for the simplified state
class HybridGraphState(TypedDict, total=False):
    question: str
    search_kwargs: dict
    docs: list[Document]
    answer: str


def advanced_rag(
    vectorstore: VectorStore | list[VectorStore],
    model_name: str,
    prompt: str | None = None,
    max_tokens: int | None = None,
    temperature: float = 0.1,
    use_preview_models: bool = False,
    enable_query_rewriting: bool = False,
    enable_rrf: bool = False,
    enable_reranking: bool = False,
    # enable_self_evaluation: bool = False,
    query_rewriting_model: str = GROQ_PRODUCTION_MODELS[0],
    query_rewriting_temperature: float = 0.1,
    rerank_model: str = "cohere-rerank-3.5",
    pinecone_api_key: str | None = None,
    rrf_constant: float = 60.0,
    rrf_weights: dict[str, float] | None = None,
    retry_config: RetryConfig | None = None,
) -> CompiledStateGraph:
    """
    Advanced Agentic RAG graph with optional query rewriting, dual-stage reranking and self-evaluation.

    :param prompt: The prompt template to use for the language model. If None, uses chATLAS_Chains.prompt.starters.CHAT_PROMPT_TEMPLATE
    :param vectorstore: Single vectorstore instance or list of vectorstore instances to search
    :param model_name: The name of the language model to use for generating responses.
    :param max_tokens: Maximum number of tokens to generate in the response. If None, uses the model's default value.
    :param temperature: Temperature to use for the model.
    :param use_preview_models: If True, allows the use of preview models from Groq.
    :param enable_query_rewriting: Whether to enable LLM-powered query rewriting.
    :param enable_rrf: Whether to enable RRF (Reciprocal Rank Fusion) for combining results from multiple vectorstores.
    :param enable_reranking: Whether to rerank the retrieved results using the Pinecone API.
    :param query_rewriting_model: Name of the model to use for query rewriting.
    :param query_rewriting_temperature: Temperature to use for query rewriting.
    :param rerank_model: Name of the Pinecone reranker model to use.
    :param pinecone_api_key: Pinecone API key. If None, will use PINECONE_API_KEY environment variable.
    :param rrf_constant: Constant to use for RRF (Reciprocal Rank Fusion) calculations.
    :param rrf_weights: How to weight the RRF score for each retriever. Default is 1.0 for all.
    :param retry_config: Optional RetryConfig for Groq API calls

    :return: A compiled LangGraph with the chosen features

    """
    if prompt is None:
        prompt = CHAT_PROMPT_TEMPLATE

    # Create prompt template
    prompt_template = ChatPromptTemplate.from_template(prompt)

    # Parallel searcher for vectorstore(s)
    searcher = search_runnable(vectorstore)

    # Initialise models
    model = get_chat_model(model_name, max_tokens, temperature, use_preview_models, retry_config)

    if enable_query_rewriting:
        query_rewriting_model_instance = get_chat_model(
            model_name=query_rewriting_model,
            temperature=query_rewriting_temperature,
            use_preview_models=use_preview_models,
        )

    # --------------- Define functions for the graph nodes ---------------

    def query_rewriting(state: HybridGraphState) -> HybridGraphState:
        """Rewrite the query to correct typos and enhance clarity."""
        question = state["question"]

        if not enable_query_rewriting:
            print("[WARNING] Query rewriting disabled, but query_rewriting node was called.")
            # return original state
            return {**state}

        rewritten_query = rewrite_query(question, model=query_rewriting_model_instance)

        return {
            **state,
            "question": rewritten_query,
            "unchanged_question": question,  # Keep original for reference
        }

    def retrieval(state: HybridGraphState) -> HybridGraphState:
        """Call the search runnable to retrieve documents"""

        question = state.get("question")
        if question is None:
            raise Exception("question field is None")

        search_kwargs = state.get("search_kwargs", {})
        if not search_kwargs:
            print("[WARNING] No search_kwargs provided, using defaults.")
            results = searcher.invoke(question)
        else:
            results = searcher.invoke(question, config={"metadata": {"search_kwargs": search_kwargs}})

        if "docs" not in results:
            raise Exception("Search results missing 'docs' field")

        print(f"Retrieved {len(results['docs'])} documents")

        return {
            **state,
            "docs": results["docs"],
        }

    # Define the document reranking function
    def rerank(state: HybridGraphState) -> HybridGraphState:
        """
        Rerank the parent documents using the Pinecone API.
        """

        if not enable_reranking:
            print("[WARNING] Reranking disabled, but rerank node was called.")
            # return original state
            return {**state}

        docs = state.get("docs", [])

        try:
            reranked_docs = rerank_documents(
                question=state["question"],
                docs=docs,
                reranker_model=rerank_model,
                api_key=pinecone_api_key,
                # num_return_docs = None # return everything
            )

        except Exception as e:
            print(f"[WARNING] Reranking failed with exception {e}. Returning original documents.")
            reranked_docs = docs

        return {
            **state,
            "docs": reranked_docs,
        }

    def rrf(state: HybridGraphState) -> HybridGraphState:
        """Perform Reciprocal Rank Fusion (RRF) on retrieved documents."""
        if not enable_rrf:
            print("[WARNING] RRF disabled, but rrf node was called.")
            # return original state
            return {**state}

        docs = state.get("docs", [])
        if not docs:
            print("[WARNING] No documents retrieved for RRF.")
            return {**state}

        try:
            rrf_docs = reciprocal_rank_fusion(
                results=split_docs_by_retriever(docs), k=rrf_constant, weights=rrf_weights
            )
        except Exception as e:
            print(f"[WARNING] RRF failed with exception {e}. Returning original documents.")
            rrf_docs = docs

        return {
            **state,
            "docs": rrf_docs,
        }

    def generate_answer(state: HybridGraphState) -> HybridGraphState:
        """Generate a response from the LLM"""

        # Format the prompt using LangChain template
        prompt_input = {"context": combine_documents(state["docs"]), "question": state["question"]}
        final_prompt = prompt_template.format_messages(**prompt_input)

        response = model.invoke(final_prompt)
        answer = response.content

        return {
            **state,
            "answer": answer,
        }

    # --------------- Build the graph ---------------
    graph = StateGraph(HybridGraphState)

    # Add all the nodes, but don't link to them if not using
    graph.add_node("query_rewrite", query_rewriting)
    graph.add_node("retrieval", retrieval)
    graph.add_node("rrf", rrf)
    graph.add_node("rerank", rerank)
    graph.add_node("generate", generate_answer)
    # graph.add_node("assess", assess_answer)
    # graph.add_node("refine", refine_answer)

    if enable_query_rewriting:
        # rewrite the query first
        graph.add_edge("query_rewrite", "retrieval")
        graph.set_entry_point("query_rewrite")
    else:
        # start with retrieval
        graph.set_entry_point("retrieval")

    if not enable_rrf and not enable_reranking:
        # no document processing, go straight to generation
        graph.add_edge("retrieval", "generate")

    elif enable_rrf and not enable_reranking:
        # retrieve → rrf → generate
        graph.add_edge("retrieval", "rrf")
        graph.add_edge("rrf", "generate")

    elif not enable_rrf and enable_reranking:
        # retrieve → rerank → generate
        graph.add_edge("retrieval", "rerank")
        graph.add_edge("rerank", "generate")

    else:
        # retrieve → rrf → rerank → generate
        graph.add_edge("retrieval", "rrf")
        graph.add_edge("rrf", "rerank")
        graph.add_edge("rerank", "generate")

    # generate at the end
    graph.add_edge("generate", END)

    # Compile the graph
    return graph.compile()


if __name__ == "__main__":
    from chATLAS_Chains.llm.model_selection import GROQ_PRODUCTION_MODELS
    from chATLAS_Chains.vectorstore import get_vectorstore

    twiki = get_vectorstore("twiki_prod")

    retry_config = RetryConfig(
        max_retries=1,
        max_delay=120.0,
    )

    # Create the hybrid graph
    graph = advanced_rag(
        vectorstore=[twiki],
        model_name=GROQ_PRODUCTION_MODELS[0],
        enable_query_rewriting=True,
        enable_rrf=True,
        enable_reranking=True,
    )

    # Test query
    try:
        ans = graph.invoke(
            {
                "question": "How can one check for and remove bad or corrupted events in the analysis?",
                "search_kwargs": {
                    "k_text": 3,
                    "k": 15,
                    "date_filter": "01-01-2010",
                    # "type": ["twiki"],
                },
            }
        )

        print(f"Number of docs is : {len(ans['docs'])}")
        print(f"Answer: {ans['answer']}")

    except Exception as e:
        print(f"❌ Graph execution failed with error: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

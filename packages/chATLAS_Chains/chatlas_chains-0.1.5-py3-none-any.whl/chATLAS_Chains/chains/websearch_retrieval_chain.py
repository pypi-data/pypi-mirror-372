"""
Example graph for running langgraph with RAG retrieval plus web search capability.
Combines database retrieval with web search results for enhanced information gathering.
"""

import json
import logging
import os
import sys
from collections.abc import Callable
from datetime import datetime
from operator import itemgetter
from pathlib import Path
from typing import Annotated, Any, Optional, TypedDict, Union

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph
from openai import OpenAI

from chATLAS_Chains.llm.model_selection import get_chat_model
from chATLAS_Chains.prompt.starters import WEB_SEARCH_CHAT_PROMPT_TEMPLATE
from chATLAS_Chains.utils.doc_utils import combine_documents
from chATLAS_Embed import LangChainVectorStore

logger = logging.getLogger(__name__)


# Define TypedDict for the state with web search support
class GraphState(TypedDict, total=False):
    question: str
    search_kwargs: dict
    retrieved_docs: dict[str, list[Document]]
    websearch_source: list[dict[str, Any]]
    merged_docs: list[Document]
    context: str
    answer: str


def web_search(query: str) -> str:
    """
    Performs a web search using OpenAI's gpt-4o-search-preview model
    and formats the result as a JSON object containing title, url, and content.

    Parameters
    ----------
    query : str
        The search query string.

    Returns
    -------
    str
        A JSON string representing the search result, or an error message in JSON format.
    """
    try:
        api_key = os.getenv("CHATLAS_OPENAI_KEY")
        if not api_key:
            raise ValueError("CHATLAS_OPENAI_KEY not set in environment")
        api_key = api_key.strip()

        client = OpenAI(api_key=api_key)

        logger.info(f"Performing web search for query: {query}")
        completion = client.chat.completions.create(
            model="gpt-4o-search-preview",
            web_search_options={"search_context_size": "low"},
            messages=[
                {
                    "role": "user",
                    "content": query,
                }
            ],
        )

        message = completion.choices[0].message
        content = message.content
        title = None
        url = None
        citations = []

        # Extract title and url from url_citation annotations
        if hasattr(message, "annotations") and message.annotations:
            for annotation in message.annotations:
                if annotation.type == "url_citation" and hasattr(annotation, "url_citation"):
                    citation = {
                        "title": getattr(annotation.url_citation, "title", None),
                        "url": getattr(annotation.url_citation, "url", None),
                    }
                    citations.append(citation)
                    # Use the first citation for main title/url if not already set
                    if title is None and url is None:
                        title = citation["title"]
                        url = citation["url"]

        result = {
            "title": title or "Web Search Result",
            "url": url or "#",
            "content": content,
            "type": "WebSearch",
            "citations": citations,
        }

        return json.dumps(result, ensure_ascii=False, indent=4)

    except Exception as e:
        logger.error(f"Web search error: {e!s}")
        error_result = {"error": str(e), "type": "WebSearchError"}
        return json.dumps(error_result, ensure_ascii=False, indent=4)


def is_low_quality_web_result(content: str) -> bool:
    """
    Detect if web search result is low quality or contains "no information" responses.

    Parameters
    ----------
    content : str
        Content of the web search result

    Returns
    -------
    bool
        True if the result is low quality and should be filtered out
    """
    content_lower = content.lower()

    # Patterns that indicate "no information" responses
    no_info_patterns = [
        "unable to locate",
        "unable to find",
        "i don't have access",
        "i cannot find",
        "no specific information",
        "not publicly available",
        "may not be publicly available",
        "i recommend the following steps",
        "contact the developers",
        "check internal documentation",
        "i may be able to assist you further",
        "if you can provide more context",
    ]

    # Check if content contains any "no information" patterns
    for pattern in no_info_patterns:
        if pattern in content_lower:
            logger.info(f"Filtering out low-quality web result containing: '{pattern}'")
            return True

    # Check if content is too short (likely not useful)
    if len(content.strip()) < 100:
        logger.info("Filtering out web result: content too short")
        return True

    return False


def process_web_search_results(query: str, results_json: str) -> list[dict[str, Any]]:
    """
    Process web search results, calculate similarity for each result and filter out low-quality results.

    Parameters
    ----------
    query : str
        Search query
    results_json : str
        JSON string returned by web_search function

    Returns
    -------
    list[dict[str, Any]]
        Processed results list, each result contains similarity field, filtered for quality
    """
    try:
        results = json.loads(results_json)

        # If it's an error result, return empty list
        if "error" in results:
            return []

        # Convert single result to list
        if not isinstance(results, list):
            results = [results]

        filtered_results = []

        # Process and filter each result
        for result in results:
            content = result.get("content", "")

            # Skip low-quality results
            if is_low_quality_web_result(content):
                continue

            # Add similarity score (placeholder, could be improved with semantic similarity)
            similarity_score = calculate_basic_similarity(query, content)
            result["similarity"] = similarity_score
            result["source_priority"] = 2  # Web search sources have lower priority

            filtered_results.append(result)

        # Sort by similarity score (descending)
        filtered_results.sort(key=lambda x: x.get("similarity", 0), reverse=True)

        logger.info(f"Processed {len(filtered_results)} web search results (filtered from {len(results)} total)")

        return filtered_results

    except Exception as e:
        logger.error(f"Error processing web search results: {e!s}")
        return []


def calculate_basic_similarity(query: str, content: str) -> float:
    """
    Calculate basic similarity between query and content based on word overlap.
    This is a simple implementation - could be improved with semantic similarity.

    Parameters
    ----------
    query : str
        Search query
    content : str
        Content to compare against

    Returns
    -------
    float
        Similarity score between 0 and 1
    """
    query_words = set(query.lower().split())
    content_words = set(content.lower().split())

    if not query_words:
        return 0.0

    overlap = len(query_words.intersection(content_words))
    return overlap / len(query_words)


def websearch_retrieval_graph(vectorstore, model_name: str, enable_web_search: bool = True) -> CompiledStateGraph:
    """
    Enhanced RAG retrieval graph using LangGraph with web search capability.
    Searches vectorstore(s), optionally performs web search, and generates answers.

    Args:
        vectorstore: the vectorstore(s) to search
        model_name: str, the name of the model to use for the response
        enable_web_search: bool, whether to enable web search functionality

    Returns:
        A LangGraph graph that can be executed for RAG with web search
    """

    # Initialize the model and prompt template
    model = get_chat_model(model_name)
    prompt_template = ChatPromptTemplate.from_template(WEB_SEARCH_CHAT_PROMPT_TEMPLATE)

    # Create a list of retrievers from the vectorstore(s)
    if isinstance(vectorstore, list):
        retrievers = [LangChainVectorStore(vector_store=vs) for vs in vectorstore]
    else:
        retrievers = [LangChainVectorStore(vector_store=vectorstore)]

    # Define the retrieval function
    def retrieve_documents(state: GraphState) -> GraphState:
        """Retrieve documents from all vectorstores."""
        question = state["question"]
        search_kwargs = state.get("search_kwargs", {})  # Get search params from state
        docs_dict = {}

        for i, retriever in enumerate(retrievers):
            try:
                docs_dict[f"docs_{i}"] = retriever.invoke(
                    question,
                    config={"metadata": {"search_kwargs": search_kwargs}},  # Pass search params to retriever
                )
                logger.info(f"Retrieved {len(docs_dict[f'docs_{i}'])} documents from vectorstore {i}")
            except Exception as e:
                logger.error(f"Error retrieving from vectorstore {i}: {e}")
                docs_dict[f"docs_{i}"] = []

        # Web search functionality
        websearch_results = []
        if enable_web_search:
            try:
                logger.info("Performing web search...")
                websearch_json = web_search(question)
                websearch_results = process_web_search_results(question, websearch_json)
                logger.info(f"Retrieved {len(websearch_results)} web search results")
            except Exception as e:
                logger.error(f"Web search failed: {e!s}")
                websearch_results = []

        return {
            "question": question,
            "search_kwargs": search_kwargs,
            "retrieved_docs": docs_dict,
            "websearch_source": websearch_results,
        }

    # Define the document merging function
    def merge_docs(state: GraphState) -> GraphState:
        """Merge all retrieved documents into a single list, including web search results."""
        docs_dict = state["retrieved_docs"]
        websearch_results = state.get("websearch_source", [])
        all_docs = []

        # Add vectorstore documents
        for i in range(len(retrievers)):
            vectorstore_docs = docs_dict.get(f"docs_{i}", [])
            all_docs.extend(vectorstore_docs)

        # Convert web search results to Document objects
        for web_result in websearch_results:
            if "content" in web_result and "error" not in web_result:
                web_doc = Document(
                    page_content=web_result["content"],
                    metadata={
                        "title": web_result.get("title", "Web Search Result"),
                        "url": web_result.get("url", "#"),
                        "type": web_result.get("type", "WebSearch"),
                        "similarity": web_result.get("similarity", 0.0),
                        "source_priority": web_result.get("source_priority", 2),
                        "citations": web_result.get("citations", []),
                        "last_modification": datetime.now().strftime("%d-%m-%Y"),  # Filler value for web search
                        "name": web_result.get("title", "Web Search Result"),
                    },
                )
                all_docs.append(web_doc)

        logger.info(f"Merged {len(all_docs)} total documents (vectorstore + web search)")

        return {
            "question": state["question"],
            "retrieved_docs": state["retrieved_docs"],
            "websearch_source": state["websearch_source"],
            "merged_docs": all_docs,
        }

    # Define the document processing function
    def process_docs(state: GraphState) -> GraphState:
        """Process the merged documents into a context string."""
        docs = state["merged_docs"]

        # Sort documents by source priority (1=internal, 2=web) and similarity
        # Internal ATLAS sources should be prioritized
        sorted_docs = sorted(
            docs,
            key=lambda x: (
                x.metadata.get("source_priority", 1),  # Internal sources first
                -x.metadata.get("similarity", 0.0),  # Then by similarity descending
            ),
        )

        context = combine_documents(sorted_docs)
        logger.info(f"Processed {len(docs)} documents into context string")

        return {
            "question": state["question"],
            "retrieved_docs": state["retrieved_docs"],
            "websearch_source": state["websearch_source"],
            "merged_docs": state["merged_docs"],
            "context": context,
        }

    # Define the answer generation function
    def generate_answer(state: GraphState) -> GraphState:
        """Generate an answer using the LLM with enhanced context including web search results."""
        question = state["question"]
        context = state["context"]

        prompt_input = {"context": context, "question": question}

        chain = prompt_template | model
        response = chain.invoke(prompt_input)

        # Extract the answer content
        answer_content = response.content if hasattr(response, "content") else str(response)

        logger.info("Generated answer using LLM")
        print("this is a test")

        return {
            "question": state["question"],
            "retrieved_docs": state["retrieved_docs"],
            "websearch_source": state["websearch_source"],
            "merged_docs": state["merged_docs"],
            "context": state["context"],
            "answer": answer_content,
        }

    # Build the graph with the defined state schema
    graph = StateGraph(GraphState)

    # Add nodes
    graph.add_node("retrieve", retrieve_documents)
    graph.add_node("merge", merge_docs)
    graph.add_node("process", process_docs)
    graph.add_node("generate", generate_answer)

    # Define the edges
    graph.add_edge("retrieve", "merge")
    graph.add_edge("merge", "process")
    graph.add_edge("process", "generate")
    graph.add_edge("generate", END)

    # Set the entry point
    graph.set_entry_point("retrieve")

    # Compile the graph
    return graph.compile()


if __name__ == "__main__":
    # Example of how to run the graph correctly
    import os

    os.environ["CHATLAS_EMBEDDING_MODEL_PATH"] = "<PATH TO YOUR EMBEDDING MODEL>"
    os.environ["CHATLAS_OPENAI_KEY"] = "YOUR OPENAI API KEY"
    os.environ["CHATLAS_DB_PASSWORD"] = "<>"
    os.environ["CHATLAS_PORT_FORWARDING"] = "true"

    from chATLAS_Chains.prompt.starters import WEB_SEARCH_CHAT_PROMPT_TEMPLATE
    from chATLAS_Chains.vectorstore import get_all_vectorstores

    graph = websearch_retrieval_graph(
        vectorstore=get_all_vectorstores(), model_name="gpt-4o-mini", enable_web_search=True
    )

    ans = graph.invoke(
        {
            "question": "How many onions are in ATLAS?",
            "search_kwargs": {
                "k_text": 3,
                "k": 10,
                "date_filter": "01-01-2010",
                "type": ["CDS", "twiki", "Indico"],
            },
        }
    )

    print(ans)

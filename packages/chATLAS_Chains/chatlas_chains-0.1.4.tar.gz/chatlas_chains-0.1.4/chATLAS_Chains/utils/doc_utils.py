import tiktoken
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate, format_document
from langchain_core.runnables import RunnableLambda

from chATLAS_Chains.llm.model_selection import get_context_window
from chATLAS_Chains.prompt.doc_joiners import DEFAULT_DOCUMENT_JOINER


def combine_documents(
    docs: list[Document], document_prompt: str = DEFAULT_DOCUMENT_JOINER, document_separator: str = "\n\n"
):
    """
    Combine a list of documents into a single formatted string.

    :param docs: The list of documents to combine.
    :type docs: list[Document]
    :param document_prompt: The prompt template used to format each document.
                            Defaults to `DEFAULT_DOCUMENT_JOINER`.
    :type document_prompt: str, optional
    :param document_separator: The separator to place between documents in the final string.
                               Defaults to two newlines.
    :type document_separator: str, optional

    :return: A single string containing all formatted documents joined by the separator.
    :rtype: str
    """

    doc_strings = [format_document(doc, PromptTemplate.from_template(document_prompt)) for doc in docs]

    return document_separator.join(doc_strings)


def truncate_to_context_window(
    docs: list[Document], question: str, prompt: ChatPromptTemplate, model_name: str, buffer: float = 0.1
) -> list[Document]:
    """
    Truncate documents to fit within the context window.

    :param docs: List of documents to truncate.
    :type docs: list[Document]
    :param question: The question to be answered, used in the prompt.
    :type question: str
    :param prompt: The prompt template to use for formatting the documents.
    :type prompt: ChatPromptTemplate
    :param model name: The model name (used to look up the context window)
    :type context_window: str
    :buffer: Buffer percentage to leave under the context window limit. Default is 0.1 (10%).

    :return: List of truncated documents.
    :rtype: list[Document]
    """

    filled_prompt = prompt.format(question=question, context=combine_documents(docs, DEFAULT_DOCUMENT_JOINER))

    encoding = tiktoken.encoding_for_model("gpt-4o-mini")
    total_tokens = len(encoding.encode(filled_prompt))

    context_window = get_context_window(model_name)

    if total_tokens >= context_window * (1 - buffer):
        # remove last doc and call again
        docs = docs[:-1]
        return truncate_to_context_window(docs, question, prompt, model_name, buffer)

    else:
        return docs

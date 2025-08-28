from operator import itemgetter
from typing import Optional

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSerializable

from chATLAS_Chains.llm.groq import RetryConfig
from chATLAS_Chains.llm.model_selection import get_chat_model
from chATLAS_Chains.search.basic import search_runnable
from chATLAS_Chains.utils.doc_utils import combine_documents
from chATLAS_Embed.Base import VectorStore


def basic_retrieval_chain(
    prompt: str,
    vectorstore: VectorStore | list[VectorStore],
    model_name: str,
    max_tokens: int | None = None,
    temperature: float | None = None,
    use_preview_models: bool = False,
    retry_config: RetryConfig | None = None,
) -> RunnableSerializable:
    """
    Baseline RAG retrieval chain. Searches one or several vectorstores in parallel, passes retrieved documents to the model

    :param prompt: The prompt template to use with the model.
    :type prompt: str
    :param vectorstore: The vectorstore or list of vectorstores to search over.
    :type vectorstore: Any
    :param model_name: The name of the chat model to use for generating responses.
    :type model_name: str
    :param max_tokens: The maximum number of tokens to generate in the response. Defaults to None.
    :type max_tokens: int | None
    :param temperature: The temperature to use for the model's response generation. Defaults to None.
    :type temperature: float | None
    :param use_preview_models: Whether to allow the use of preview models from Groq. Defaults to False.
    :type use_preview_models: bool
    :param retry_config: Configuration for retrying requests to the model in case of failures. Defaults to None, which will use the default retry configuration.
    :type retry_config: RetryConfig | None

    :return: A LangChain RunnableSerializable chain that performs retrieval and response generation.
    :rtype: RunnableSerializable

    """
    prompt_template = ChatPromptTemplate.from_template(prompt)
    model = get_chat_model(model_name, max_tokens, temperature, use_preview_models, retry_config)

    search = search_runnable(vectorstore)

    final_inputs = {
        "context": lambda x: combine_documents(x["docs"]),
        "question": itemgetter("question"),
    }

    answer = {
        "answer": final_inputs | prompt_template | model,
        "docs": lambda x: x["docs"],
    }

    chain = search | answer
    return chain


if __name__ == "__main__":
    from chATLAS_Chains.llm.model_selection import GROQ_PRODUCTION_MODELS
    from chATLAS_Chains.prompt.starters import CHAT_PROMPT_TEMPLATE
    from chATLAS_Chains.vectorstore import get_vectorstore

    twiki_vectorstore = get_vectorstore("twiki_prod")
    mkdocs_vectorstore = get_vectorstore("mkdocs_prod_v1")

    chain = basic_retrieval_chain(
        prompt=CHAT_PROMPT_TEMPLATE,
        vectorstore=[twiki_vectorstore, mkdocs_vectorstore],
        model_name=GROQ_PRODUCTION_MODELS[0],
        # model_name="meta-llama/llama-4-maverick-17b-128e-instruct",
        # model_name="gemma2-9b-it",
        # model_name="qwen-qwq-32b",
        # model_name="mistral-saba-24b",
    )
    SEARCH_HYPERPARAMS = {"k": 5, "k_text": 0, "date_filter": "01-01-2010"}

    result = chain.invoke("What is the Higgs boson?", config={"metadata": {"search_kwargs": SEARCH_HYPERPARAMS}})

    print(f"Answer: {result['answer'].content}")
    print(f"Number of documents retrieved: {len(result['docs'])}")

    for doc in result["docs"]:
        print(doc.metadata.get("source"))

"""
Contains code for rewriting user queries to aid retrieval
"""

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate

QUERY_REWRITING_PROMPT = """You are a helpful assistant tasked with revising a sentence by correcting any 
            typos and improving the wording for clarity and natural flow in English. 
            If a typo is intentional or acceptable, 
            leave it unchanged. Provide only one revised version of the sentence. 
            Do not include explanations or alternatives.
            
            IMPORTANT CONSTRAINTS:
            - Output ONLY the rewritten query text
            - Do NOT include any prefixes like "Rewritten version:", "Revised:", "Answer:", etc.
            - Do NOT include any explanations, notes, or commentary
            - Do NOT include quotation marks around the output
            - Just output the improved query directly
            
            Question: {question}
            """


def rewrite_query(question: str, model: BaseChatModel, rewrite_prompt: str = QUERY_REWRITING_PROMPT) -> str:
    """
    Rewrite the user query to improve clarity and correctness.

    :param question: The original user query to be rewritten.
    :type question: str
    :param model: The chat model used for rewriting the query.
    :type model: BaseChatModel
    :param rewrite_prompt: The prompt template for rewriting the query.
    :type rewrite_prompt: str

    :return: The rewritten query.
    :rtype: str
    """
    rewrite_prompt_template = ChatPromptTemplate.from_template(rewrite_prompt)

    response = model.invoke(rewrite_prompt_template.format(question=question))

    return str(response.content)


if __name__ == "__main__":
    # Example usage
    from chATLAS_Chains.llm.model_selection import GROQ_PRODUCTION_MODELS, get_chat_model

    llm = get_chat_model(model_name=GROQ_PRODUCTION_MODELS[0])

    question = "What is the Drell-Yan dilepton cross section?"
    print(f"Original question: {question}")

    rewritten = rewrite_query(question, llm)
    print(f"Rewritten question: {rewritten}")

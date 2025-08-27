import importlib
import os

from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from chATLAS_Chains.llm.groq import AccGPTChatGroq, RetryConfig

OPENAI_MODELS = ["gpt-3.5-turbo", "gpt-4", "gpt-4o", "gpt-4o-mini"]

# see Groq docs: https://console.groq.com/docs/models
GROQ_PRODUCTION_MODELS = [
    "llama-3.1-8b-instant",
    "llama-3.3-70b-versatile",
    "meta-llama/llama-guard-4-12b",
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    # "whisper-large-v3", # audio to text model
    # "whisper-large-v3-turbo" # audio to text model
]

GROQ_PREVIEW_MODELS = [
    "deepseek-r1-distill-llama-70b",
    "meta-llama/llama-4-maverick-17b-128e-instruct",
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "meta-llama/llama-prompt-guard-2-22m",
    "meta-llama/llama-prompt-guard-2-86m",
    "moonshotai/kimi-k2-instruct",
    # "playai-tts",  # text to audio model
    # "playai-tts-arabic",  # text to audio model
    "qwen/qwen3-32b",
    "gemma2-9b-it",
]

GROQ_CONTEXT_WINDOWS = {
    "default": 131_072,  # most models
    "gemma2-9b-it": 8192,
    "meta-llama/llama-prompt-guard-2-22m": 512,
    "meta-llama/llama-prompt-guard-2-86m": 512,
}

GROQ_MAX_COMPLETION_TOKENS = {
    "default": 131_072,
    "llama-3.3-70b-versatile": 32_768,
    "meta-llama/llama-guard-4-12b": 1_024,
    "meta-llama/llama-4-maverick-17b-128e-instruct": 8192,
    "meta-llama/llama-4-scout-17b-16e-instruct": 8192,
    "meta-llama/llama-prompt-guard-2-22m": 512,
    "meta-llama/llama-prompt-guard-2-86m": 512,
    "moonshotai/kimi-k2-instruct": 16_384,
    "openai/gpt-oss-120b": 32_768,
    "openai/gpt-oss-20b": 32_768,
    "qwen/qwen3-32b": 40_960,
}

GROQ_MODELS = GROQ_PRODUCTION_MODELS + GROQ_PREVIEW_MODELS

SUPPORTED_CHAT_MODELS = OPENAI_MODELS + GROQ_MODELS


def get_context_window(model_name: str) -> int:
    """
    Get the context window size for a given model.
    """
    if model_name not in GROQ_CONTEXT_WINDOWS:
        model_name = "default"

    return GROQ_CONTEXT_WINDOWS[model_name]


def get_max_completion_tokens(model_name: str) -> int:
    """
    Get the max completion tokens for a given model.
    """
    if model_name not in GROQ_MAX_COMPLETION_TOKENS:
        model_name = "default"

    return GROQ_MAX_COMPLETION_TOKENS[model_name]


def get_chat_model(
    model_name,
    max_tokens: int | None = None,
    temperature: float | None = None,
    use_preview_models: bool = False,
    retry_config: RetryConfig | None = None,
):
    """
    Initialize chat model with the provided model name (if supported)

    :param model_name: The name of the model to load (e.g., "gpt-4o-mini" (OpenAI), "meta-llama/llama-4-maverick-17b-128e-instruct" (Groq)).
    :type model_name: str

    :param max_tokens: Maximum number of tokens to generate in the response. Defaults to None, which uses the model's default value.
    :type max_tokens: int | None

    :param temperature: Sampling temperature to use for the model. Defaults to None, which uses the model's default value.
    :type temperature: float | None

    :param use_preview_models: If True, allows the use of preview models from Groq. Defaults to False.
    :type use_preview_models: bool

    :raises ValueError: If the environment variable `CHATLAS_OPENAI_KEY` is not set when using OpenAI models, or if `CHATLAS_GROQ_KEY` and `CHATLAS_GROQ_BASE_URL` are not set when using Groq models.

    :return: An instance of the specified chat model.
    :rtype: BaseLanguageModel
    """

    if model_name not in SUPPORTED_CHAT_MODELS:
        raise ValueError(f"Model '{model_name}' is not supported. Supported models are: {SUPPORTED_CHAT_MODELS}")

    elif model_name in OPENAI_MODELS:
        api_key = os.getenv("CHATLAS_OPENAI_KEY")
        if not api_key or not api_key.strip():
            raise ValueError("CHATLAS_OPENAI_KEY not set in environment")

        api_key = api_key.strip()
        llm = ChatOpenAI(
            model_name=model_name,
            openai_api_key=SecretStr(api_key),
        )

    else:  # GROQ
        if not use_preview_models and model_name in GROQ_PREVIEW_MODELS:
            raise ValueError(f"Model '{model_name}' is a preview model. Set 'use_preview_models=True' to use it.")

        api_key = os.getenv("CHATLAS_GROQ_KEY")
        if not api_key or not api_key.strip():
            raise ValueError("CHATLAS_GROQ_KEY not set in environment")

        base_url = os.getenv("CHATLAS_GROQ_BASE_URL")
        if not base_url or not base_url.strip():
            raise ValueError("CHATLAS_GROQ_BASE_URL not set in environment")

        api_key = api_key.strip()
        base_url = base_url.strip()

        if max_tokens is None:
            max_tokens = get_max_completion_tokens(model_name)

        elif max_tokens > get_max_completion_tokens(model_name):
            raise ValueError(
                f"max_tokens ({max_tokens}) exceeds the model's maximum ({get_max_completion_tokens(model_name)})."
            )

        # default retry config
        if retry_config is None:
            retry_config = RetryConfig()

        llm = AccGPTChatGroq(
            model_name=model_name,
            api_key=api_key,
            base_url=base_url,
            max_tokens=max_tokens,
            temperature=temperature,
            retry_config=retry_config,
        )

    return llm


if __name__ == "__main__":
    message = "What is the Higgs mechanism?"

    # Example usage
    models = ["gpt-4o-mini", "gemma2-9b-it"]
    for model_name in models:
        llm = get_chat_model(model_name, max_tokens=150)
        print(f"Successfully loaded model: {model_name}")
        result = llm.invoke(message)
        print(f"result ({model_name}): {result}")
        print(f"type(result) ({model_name}): {type(result)}")

import os
from unittest.mock import MagicMock, patch

import pytest
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from chATLAS_Chains.llm.groq import AccGPTChatGroq, RetryConfig
from chATLAS_Chains.llm.model_selection import (
    GROQ_MODELS,
    GROQ_PREVIEW_MODELS,
    GROQ_PRODUCTION_MODELS,
    OPENAI_MODELS,
    SUPPORTED_CHAT_MODELS,
    get_chat_model,
    get_max_completion_tokens,
)


class TestModelSelection:
    """Test suite for model_selection.py functionality."""

    @pytest.fixture
    def mock_env_variables(self, monkeypatch):
        """Set mock environment variables for testing."""
        monkeypatch.setenv("CHATLAS_OPENAI_KEY", "fake-openai-key")
        monkeypatch.setenv("CHATLAS_GROQ_KEY", "fake-groq-key")
        monkeypatch.setenv("CHATLAS_GROQ_BASE_URL", "http://fake-groq-url.com")

    @pytest.fixture
    def mock_chat_openai(self):
        """Mock the ChatOpenAI class."""
        mock_instance = MagicMock(name="MockChatOpenAI")
        with patch("chATLAS_Chains.llm.model_selection.ChatOpenAI", return_value=mock_instance) as mock:
            yield mock, mock_instance

    @pytest.fixture
    def mock_groq(self):
        """Mock the AccGPTChatGroq class."""
        mock_instance = MagicMock(name="MockGroqModel")
        with patch("chATLAS_Chains.llm.model_selection.AccGPTChatGroq", return_value=mock_instance) as mock:
            yield mock, mock_instance

    # Test valid model initialization
    @pytest.mark.parametrize("model_name", OPENAI_MODELS)
    def test_get_openai_model(self, model_name, mock_env_variables, mock_chat_openai):
        """Test that OpenAI models are correctly initialized."""
        mock_class, mock_instance = mock_chat_openai

        model = get_chat_model(model_name)

        mock_class.assert_called_once_with(
            model_name=model_name,
            openai_api_key=SecretStr("fake-openai-key"),
        )
        assert model is mock_instance

    @pytest.mark.parametrize("model_name", GROQ_MODELS)
    def test_get_groq_model(self, model_name, mock_env_variables, mock_groq):
        """Test that Groq models are correctly initialized."""
        mock_class, mock_instance = mock_groq

        model = get_chat_model(model_name, use_preview_models=True)

        mock_class.assert_called_once_with(
            model_name=model_name,
            api_key="fake-groq-key",
            base_url="http://fake-groq-url.com",
            max_tokens=get_max_completion_tokens(model_name),
            temperature=None,
            retry_config=RetryConfig(),
        )
        assert model is mock_instance

    def test_unsupported_model(self, mock_env_variables):
        """Test that an unsupported model raises a ValueError."""
        with pytest.raises(ValueError, match=r"Model 'unsupported-model' is not supported"):
            get_chat_model("unsupported-model")

    @pytest.mark.parametrize("preview_model", GROQ_PREVIEW_MODELS)
    def test_preview_model_handling(self, preview_model, mock_env_variables, mock_groq):
        """Test handling of cases when preview models are requested."""
        mock_class, mock_instance = mock_groq

        # by default, use_preview_models is False, so this should raise an error
        with pytest.raises(
            ValueError, match=f"Model '{preview_model}' is a preview model. Set 'use_preview_models=True' to use it."
        ):
            get_chat_model(preview_model)

        # when use_preview_models is True, it should succeed
        model = get_chat_model(preview_model, use_preview_models=True)

        mock_class.assert_called_once_with(
            model_name=preview_model,
            api_key="fake-groq-key",
            base_url="http://fake-groq-url.com",
            max_tokens=get_max_completion_tokens(preview_model),
            temperature=None,
            retry_config=RetryConfig(),
        )
        assert model is mock_instance

    def test_missing_openai_key(self, monkeypatch):
        """Test error when OPENAI_KEY is missing."""
        # Ensure environment variable doesn't exist
        monkeypatch.delenv("CHATLAS_OPENAI_KEY", raising=False)

        with pytest.raises(ValueError, match="CHATLAS_OPENAI_KEY not set in environment"):
            get_chat_model("gpt-4")

    def test_empty_openai_key(self, monkeypatch):
        """Test error when OPENAI_KEY is empty."""

        monkeypatch.setenv("CHATLAS_OPENAI_KEY", "   ")

        with patch(
            "os.getenv", side_effect=lambda key, default=None: None if key == "CHATLAS_OPENAI_KEY" else "fake-value"
        ):
            with pytest.raises(ValueError, match="CHATLAS_OPENAI_KEY not set in environment"):
                get_chat_model("gpt-4")

    def test_missing_groq_key(self, monkeypatch):
        """Test error when GROQ_KEY is missing."""
        monkeypatch.setenv("CHATLAS_GROQ_BASE_URL", "http://fake-groq-url.com")
        monkeypatch.delenv("CHATLAS_GROQ_KEY", raising=False)

        with pytest.raises(ValueError, match="CHATLAS_GROQ_KEY not set in environment"):
            get_chat_model(GROQ_PRODUCTION_MODELS[0])

    def test_missing_groq_base_url(self, monkeypatch):
        """Test error when GROQ_BASE_URL is missing."""
        monkeypatch.setenv("CHATLAS_GROQ_KEY", "fake-groq-key")
        monkeypatch.delenv("CHATLAS_GROQ_BASE_URL", raising=False)

        with pytest.raises(ValueError, match="CHATLAS_GROQ_BASE_URL not set in environment"):
            get_chat_model(GROQ_PRODUCTION_MODELS[0])

    def test_empty_groq_key(self, monkeypatch):
        """Test error when GROQ_KEY is empty."""
        # We need to patch os.getenv for whitespace values similar to the OpenAI test
        with patch(
            "os.getenv",
            side_effect=lambda key, default=None: None
            if key == "CHATLAS_GROQ_KEY"
            else "http://fake-groq-url.com"
            if key == "CHATLAS_GROQ_BASE_URL"
            else "fake-value",
        ):
            monkeypatch.setenv("CHATLAS_GROQ_KEY", "  ")
            monkeypatch.setenv("CHATLAS_GROQ_BASE_URL", "http://fake-groq-url.com")

            with pytest.raises(ValueError, match="CHATLAS_GROQ_KEY not set in environment"):
                get_chat_model(GROQ_PRODUCTION_MODELS[0])

    def test_empty_groq_base_url(self, monkeypatch):
        """Test error when GROQ_BASE_URL is empty."""
        # Similar patching for empty base URL
        with patch(
            "os.getenv",
            side_effect=lambda key, default=None: "fake-groq-key"
            if key == "CHATLAS_GROQ_KEY"
            else None
            if key == "CHATLAS_GROQ_BASE_URL"
            else "fake-value",
        ):
            monkeypatch.setenv("CHATLAS_GROQ_KEY", "fake-groq-key")
            monkeypatch.setenv("CHATLAS_GROQ_BASE_URL", "  ")

            with pytest.raises(ValueError, match="CHATLAS_GROQ_BASE_URL not set in environment"):
                get_chat_model(GROQ_PRODUCTION_MODELS[0])

    # Test key stripping
    def test_openai_key_stripped(self, monkeypatch, mock_chat_openai):
        """Test that whitespace is stripped from OpenAI API key."""
        mock_class, _ = mock_chat_openai
        monkeypatch.setenv("CHATLAS_OPENAI_KEY", "  whitespace-key  ")

        get_chat_model("gpt-4")

        mock_class.assert_called_once_with(
            model_name="gpt-4",
            openai_api_key=SecretStr("whitespace-key"),
        )

    def test_groq_key_and_url_stripped(self, monkeypatch, mock_groq):
        """Test that whitespace is stripped from Groq API key and base URL."""
        mock_class, _ = mock_groq
        monkeypatch.setenv("CHATLAS_GROQ_KEY", "  whitespace-groq-key  ")
        monkeypatch.setenv("CHATLAS_GROQ_BASE_URL", "  http://whitespace-url.com  ")

        get_chat_model(GROQ_PRODUCTION_MODELS[0])

        mock_class.assert_called_once_with(
            model_name=GROQ_PRODUCTION_MODELS[0],
            api_key="whitespace-groq-key",
            base_url="http://whitespace-url.com",
            max_tokens=get_max_completion_tokens(GROQ_PRODUCTION_MODELS[0]),
            temperature=None,
            retry_config=RetryConfig(),
        )

    def test_supported_models_lists(self):
        """Test that SUPPORTED_CHAT_MODELS is correctly composed of OPENAI_MODELS and GROQ_MODELS."""
        assert set(SUPPORTED_CHAT_MODELS) == set(OPENAI_MODELS + GROQ_MODELS)

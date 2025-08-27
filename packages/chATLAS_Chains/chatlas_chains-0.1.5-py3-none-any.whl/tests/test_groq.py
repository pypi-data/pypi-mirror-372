import json
import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime
from typing import cast
from unittest.mock import MagicMock, Mock, call, patch

import pytest
import requests
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from requests.exceptions import ConnectionError, Timeout

from chATLAS_Chains.llm.groq import (
    AccGPTChatGroq,
    GroqAPIError,
    RateLimitInfo,
    RetryConfig,
)


class TestRateLimitInfo:
    """Test the RateLimitInfo dataclass"""

    def test_rate_limit_info_initialization(self):
        """Test that RateLimitInfo initializes with default values"""
        info = RateLimitInfo()
        assert info.requests_limit is None
        assert info.tokens_limit is None
        assert info.requests_remaining is None
        assert info.tokens_remaining is None
        assert info.requests_reset_time is None
        assert info.tokens_reset_time is None
        assert info.retry_after is None

    def test_rate_limit_info_with_values(self):
        """Test RateLimitInfo with specific values"""
        info = RateLimitInfo(
            requests_limit=1000,
            tokens_limit=5000,
            requests_remaining=500,
            tokens_remaining=2500,
            requests_reset_time=3600.0,
            tokens_reset_time=300.0,
            retry_after=60,
        )
        assert info.requests_limit == 1000
        assert info.tokens_limit == 5000
        assert info.requests_remaining == 500
        assert info.tokens_remaining == 2500
        assert info.requests_reset_time == 3600.0
        assert info.tokens_reset_time == 300.0
        assert info.retry_after == 60


class TestRetryConfig:
    """Test the RetryConfig dataclass"""

    def test_retry_config_defaults(self):
        """Test that RetryConfig initializes with correct defaults"""
        config = RetryConfig()
        assert config.max_retries == 0
        assert config.base_delay == 1.0
        assert config.max_delay == 60.0
        assert config.exponential_base == 2.0
        assert config.jitter is True
        assert config.respect_rate_limits is True

    def test_retry_config_custom_values(self):
        """Test RetryConfig with custom values"""
        config = RetryConfig(
            max_retries=5,
            base_delay=2.0,
            max_delay=120.0,
            exponential_base=1.5,
            jitter=False,
            respect_rate_limits=False,
        )
        assert config.max_retries == 5
        assert config.base_delay == 2.0
        assert config.max_delay == 120.0
        assert config.exponential_base == 1.5
        assert config.jitter is False
        assert config.respect_rate_limits is False


class TestGroqAPIError:
    """Test the GroqAPIError exception class"""

    def test_groq_api_error_basic(self):
        """Test basic GroqAPIError initialization"""
        error = GroqAPIError("Test error message")
        assert str(error) == "Test error message"
        assert error.response_data is None
        assert error.status_code is None
        assert error.is_retryable is False
        assert error.rate_limit_info is None

    def test_groq_api_error_full(self):
        """Test GroqAPIError with all parameters"""
        response_data = {"error": "API error"}
        rate_limit_info = RateLimitInfo(retry_after=30)

        error = GroqAPIError(
            message="Full error",
            response_data=response_data,
            status_code=429,
            is_retryable=True,
            rate_limit_info=rate_limit_info,
        )

        assert str(error) == "Full error"
        assert error.response_data == response_data
        assert error.status_code == 429
        assert error.is_retryable is True
        assert error.rate_limit_info == rate_limit_info


class TestAccGPTChatGroq:
    """Test the main AccGPTChatGroq class"""

    @pytest.fixture
    def groq_client(self):
        """Create a test instance of AccGPTChatGroq"""
        return AccGPTChatGroq(
            base_url="http://test-server.com",
            api_key="test-api-key",
            model_name="test-model",
            temperature=0.7,
            max_tokens=100,
            timeout=30,
            debug=True,
        )

    @pytest.fixture
    def sample_messages(self):
        """Create sample messages for testing"""
        return [
            SystemMessage(content="You are a helpful assistant."),
            HumanMessage(content="What is AI?"),
            AIMessage(content="AI stands for Artificial Intelligence."),
        ]

    def test_initialization(self, groq_client):
        """Test proper initialization of AccGPTChatGroq"""
        assert groq_client.base_url.get_secret_value() == "http://test-server.com"
        assert groq_client.api_key.get_secret_value() == "test-api-key"
        assert groq_client.model_name == "test-model"
        assert groq_client.temperature == 0.7
        assert groq_client.max_tokens == 100
        assert groq_client.timeout == 30
        assert groq_client.debug is True

    def test_llm_type_property(self, groq_client):
        """Test the _llm_type property"""
        assert groq_client._llm_type == "test-model"

    def test_stream_not_implemented(self, groq_client):
        """Test that streaming raises NotImplementedError"""
        with pytest.raises(NotImplementedError):
            groq_client._stream()

    def test_parse_time_duration_valid_formats(self, groq_client):
        """Test parsing of various valid time duration formats"""
        # Test seconds only
        assert groq_client._parse_time_duration("30.5s") == 30.5
        assert groq_client._parse_time_duration("5s") == 5.0

        # Test minutes and seconds
        assert groq_client._parse_time_duration("2m30s") == 150.0
        assert groq_client._parse_time_duration("1m") == 60.0

        # Test hours, minutes, and seconds
        assert groq_client._parse_time_duration("1h30m45s") == 5445.0
        assert groq_client._parse_time_duration("2h") == 7200.0

        # Test with decimals
        assert groq_client._parse_time_duration("2m59.56s") == 179.56

    def test_parse_time_duration_invalid_formats(self, groq_client):
        """Test parsing of invalid time duration formats"""
        assert groq_client._parse_time_duration("invalid") == 0.0
        assert groq_client._parse_time_duration("") == 0.0
        assert groq_client._parse_time_duration("abc123") == 0.0

    def test_parse_rate_limit_headers_complete(self, groq_client):
        """Test parsing complete rate limit headers"""
        headers = {
            "retry-after": "30",
            "x-ratelimit-limit-requests": "1000",
            "x-ratelimit-remaining-requests": "500",
            "x-ratelimit-reset-requests": "1h30m",
            "x-ratelimit-limit-tokens": "5000",
            "x-ratelimit-remaining-tokens": "2500",
            "x-ratelimit-reset-tokens": "10m30s",
        }

        info = groq_client._parse_rate_limit_headers(headers)

        assert info.retry_after == 30
        assert info.requests_limit == 1000
        assert info.requests_remaining == 500
        assert info.requests_reset_time == 5400.0  # 1h30m
        assert info.tokens_limit == 5000
        assert info.tokens_remaining == 2500
        assert info.tokens_reset_time == 630.0  # 10m30s

    def test_parse_rate_limit_headers_partial(self, groq_client):
        """Test parsing partial rate limit headers"""
        headers = {"retry-after": "15", "x-ratelimit-remaining-requests": "100"}

        info = groq_client._parse_rate_limit_headers(headers)

        assert info.retry_after == 15
        assert info.requests_remaining == 100
        assert info.requests_limit is None
        assert info.tokens_limit is None

    def test_parse_rate_limit_headers_invalid(self, groq_client):
        """Test parsing invalid rate limit headers"""
        headers = {"retry-after": "invalid", "x-ratelimit-limit-requests": "not-a-number"}

        # Should not raise exception, just return empty info
        info = groq_client._parse_rate_limit_headers(headers)
        assert info.retry_after is None
        assert info.requests_limit is None

    def test_log_rate_limit_info_debug_off(self, groq_client):
        """Test that rate limit info is not logged when debug is off"""
        groq_client.debug = False
        info = RateLimitInfo(requests_remaining=100, requests_limit=1000)

        # This should just return without doing anything since debug=False
        groq_client._log_rate_limit_info(info)  # Should not raise any errors

    def test_log_rate_limit_info_debug_on(self, groq_client):
        """Test that rate limit info is logged when debug is on"""
        groq_client.debug = True
        info = RateLimitInfo(
            requests_remaining=100,
            requests_limit=1000,
            requests_reset_time=300.0,
            tokens_remaining=500,
            tokens_limit=2000,
            tokens_reset_time=60.0,
            retry_after=30,
        )

        # Patch the logger in the correct module
        with patch("chATLAS_Chains.llm.groq.logger") as mock_logger:
            groq_client._log_rate_limit_info(info)
            # Should have called debug at least once
            assert mock_logger.debug.call_count >= 1

    def test_calculate_rate_limit_delay_respect_off(self, groq_client):
        """Test rate limit delay calculation when respect_rate_limits is False"""
        groq_client.retry_config.respect_rate_limits = False
        info = RateLimitInfo(retry_after=30)

        delay = groq_client._calculate_rate_limit_delay(info)
        assert delay == 0.0, "If not respecting rate limits, delay should be 0"

    def test_calculate_rate_limit_delay_retry_after(self, groq_client):
        """Test rate limit delay respects retry-after header"""
        info = RateLimitInfo(retry_after=45)

        delay = groq_client._calculate_rate_limit_delay(info)
        assert delay == 45.0

    def test_calculate_rate_limit_delay_low_tokens(self, groq_client):
        """Test rate limit delay for low token availability"""

        # cap higher than reset time so we don't hit it
        groq_client.retry_config.max_delay = 200.0

        info = RateLimitInfo(
            tokens_remaining=50,  # 5% of 1000
            tokens_limit=1000,
            tokens_reset_time=120.0,
        )

        delay = groq_client._calculate_rate_limit_delay(info)
        assert delay == 121.0, "Delay should equal tokens reset time + 1 second buffer"

    def test_calculate_rate_limit_delay_low_requests(self, groq_client):
        """Test rate limit delay for low request availability"""

        # cap higher than reset time so we don't hit it
        groq_client.retry_config.max_delay = 200.0

        info = RateLimitInfo(
            requests_remaining=20,  # 2% of 1000
            requests_limit=1000,
            requests_reset_time=180.0,
        )

        delay = groq_client._calculate_rate_limit_delay(info)
        assert delay == 181.0, "Delay should rate limit reset time + 1 second buffer"

    def test_calculate_rate_limit_delay_max_delay_cap(self, groq_client):
        """Test that rate limit delay is capped at max_delay"""
        groq_client.retry_config.max_delay = 100.0
        info = RateLimitInfo(retry_after=200)

        delay = groq_client._calculate_rate_limit_delay(info)
        assert delay == 100.0  # Capped at max_delay

    def test_is_retryable_error_rate_limit(self, groq_client):
        """Test that 429 status code is always retryable"""
        info = RateLimitInfo()
        assert groq_client._is_retryable_error(429, "Rate limit exceeded", info) is True

    def test_is_retryable_error_server_errors(self, groq_client):
        """Test that server error status codes are retryable"""
        info = RateLimitInfo()
        retryable_codes = [500, 502, 503, 504]

        for code in retryable_codes:
            assert groq_client._is_retryable_error(code, "Server error", info) is True

    def test_is_retryable_error_client_errors(self, groq_client):
        """Test that client error status codes are not retryable"""
        info = RateLimitInfo()
        non_retryable_codes = [400, 401, 403, 404]

        for code in non_retryable_codes:
            assert groq_client._is_retryable_error(code, "Client error", info) is False

    def test_is_retryable_error_patterns(self, groq_client):
        """Test that specific error message patterns are retryable"""
        info = RateLimitInfo()
        retryable_messages = [
            "service unavailable",
            "temporarily unavailable",
            "timeout occurred",
            "rate limit exceeded",
            "server error detected",
        ]

        for message in retryable_messages:
            assert groq_client._is_retryable_error(200, message, info) is True

    def test_calculate_delay_exponential_backoff(self, groq_client):
        """Test exponential backoff delay calculation"""
        groq_client.retry_config.base_delay = 1.0
        groq_client.retry_config.exponential_base = 2.0
        groq_client.retry_config.jitter = False

        # Test exponential progression
        assert groq_client._calculate_delay(0) == 1.0  # 1 * 2^0
        assert groq_client._calculate_delay(1) == 2.0  # 1 * 2^1
        assert groq_client._calculate_delay(2) == 4.0  # 1 * 2^2

    def test_calculate_delay_max_delay_cap(self, groq_client):
        """Test that delay is capped at max_delay"""
        groq_client.retry_config.base_delay = 10.0
        groq_client.retry_config.exponential_base = 10.0
        groq_client.retry_config.max_delay = 50.0
        groq_client.retry_config.jitter = False

        delay = groq_client._calculate_delay(3)  # Would be 10 * 10^3 = 10000 without cap
        assert delay == 50.0

    def test_calculate_delay_with_rate_limit_info(self, groq_client):
        """Test delay calculation with rate limit information"""
        groq_client.retry_config.base_delay = 1.0
        groq_client.retry_config.jitter = False

        rate_limit_info = RateLimitInfo(retry_after=10)

        # Rate limit delay should take precedence
        delay = groq_client._calculate_delay(0, rate_limit_info)
        assert delay == 10.0

    def test_calculate_delay_jitter(self, groq_client):
        """Test that jitter adds randomness to delay"""
        groq_client.retry_config.base_delay = 4.0
        groq_client.retry_config.exponential_base = 1.0  # No exponential growth
        groq_client.retry_config.jitter = True

        delays = [groq_client._calculate_delay(0) for _ in range(10)]

        # All delays should be different due to jitter
        assert len(set(delays)) > 1
        # All delays should be around 4.0 (±25%)
        for delay in delays:
            assert 3.0 <= delay <= 5.0

    @patch("chATLAS_Chains.llm.groq.requests.post")
    def test_make_api_request_success(self, mock_post, groq_client, sample_messages):
        """Test successful API request"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"choices": [{"message": {"content": "Test response content"}}]}
        mock_response.headers = {"x-ratelimit-remaining-requests": "999", "x-ratelimit-limit-requests": "1000"}
        mock_post.return_value = mock_response

        result = groq_client._make_api_request(sample_messages, "test-model")

        assert isinstance(result, ChatResult)
        assert len(result.generations) == 1
        assert isinstance(result.generations[0].message, AIMessage)
        assert result.generations[0].message.content == "Test response content"

    @patch("chATLAS_Chains.llm.groq.requests.post")
    def test_make_api_request_json_decode_error(self, mock_post, groq_client, sample_messages):
        """Test API request with JSON decode error"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "test", 0)
        mock_response.text = "Invalid JSON response"
        # FIX: Mock headers as a proper dict instead of leaving it as Mock
        mock_response.headers = {}
        mock_post.return_value = mock_response

        with pytest.raises(GroqAPIError) as exc_info:
            groq_client._make_api_request(sample_messages, "test-model")

        exc = cast(GroqAPIError, exc_info.value)  # fix type checking
        assert "Failed to parse JSON response" in str(exc)
        assert exc.is_retryable is True

    @patch("chATLAS_Chains.llm.groq.requests.post")
    def test_make_api_request_http_error(self, mock_post, groq_client, sample_messages):
        """Test API request with HTTP error"""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.json.return_value = {"error": "Rate limit exceeded"}
        mock_response.headers = {"retry-after": "30"}
        mock_post.return_value = mock_response

        with pytest.raises(GroqAPIError) as exc_info:
            groq_client._make_api_request(sample_messages, "test-model")

        exc = cast(GroqAPIError, exc_info.value)  # fix type checking
        assert exc.status_code == 429
        assert exc.is_retryable is True

    @patch("chATLAS_Chains.llm.groq.requests.post")
    def test_make_api_request_missing_choices(self, mock_post, groq_client, sample_messages):
        """Test API request with missing choices field"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"error": "No choices"}
        mock_response.headers = {}
        mock_post.return_value = mock_response

        with pytest.raises(GroqAPIError) as exc_info:
            groq_client._make_api_request(sample_messages, "test-model")

        assert "Response missing 'choices' field" in str(exc_info.value)

    @patch("chATLAS_Chains.llm.groq.requests.post")
    def test_make_api_request_invalid_choices(self, mock_post, groq_client, sample_messages):
        """Test API request with invalid choices field"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"choices": []}  # Empty choices
        mock_response.headers = {}
        mock_post.return_value = mock_response

        with pytest.raises(GroqAPIError) as exc_info:
            groq_client._make_api_request(sample_messages, "test-model")

        exc = cast(GroqAPIError, exc_info.value)  # fix type checking
        assert "Invalid 'choices' field" in str(exc)

    @patch("chATLAS_Chains.llm.groq.requests.post")
    def test_make_api_request_network_error(self, mock_post, groq_client, sample_messages):
        """Test API request with network error"""
        mock_post.side_effect = ConnectionError("Connection failed")

        with pytest.raises(GroqAPIError) as exc_info:
            groq_client._make_api_request(sample_messages, "test-model")

        exc = cast(GroqAPIError, exc_info.value)  # fix type checking
        assert "Network error" in str(exc)
        assert exc.is_retryable is True

    @patch("chATLAS_Chains.llm.groq.requests.post")
    def test_make_api_request_timeout(self, mock_post, groq_client, sample_messages):
        """Test API request with timeout"""
        mock_post.side_effect = Timeout("Request timed out")

        with pytest.raises(GroqAPIError) as exc_info:
            groq_client._make_api_request(sample_messages, "test-model")

        exc = cast(GroqAPIError, exc_info.value)  # fix type checking
        assert "Network error" in str(exc)
        assert exc.is_retryable is True

    @patch("chATLAS_Chains.llm.groq.requests.post")
    @patch("chATLAS_Chains.llm.groq.time.sleep")
    def test_make_api_request_retry_logic(self, mock_sleep, mock_post, groq_client, sample_messages):
        """Test retry logic for retryable errors"""
        groq_client.retry_config.max_retries = 2

        # First call fails with retryable error
        mock_response_fail = Mock()
        mock_response_fail.status_code = 503
        mock_response_fail.json.return_value = {"error": "Service unavailable"}
        mock_response_fail.headers = {}

        # Second call succeeds
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {"choices": [{"message": {"content": "Success"}}]}
        mock_response_success.headers = {}

        mock_post.side_effect = [mock_response_fail, mock_response_success]

        result = groq_client._make_api_request(sample_messages, "test-model")

        assert mock_post.call_count == 2
        assert mock_sleep.call_count == 1  # Should sleep before retry
        assert result.generations[0].message.content == "Success"

    def test_analyze_response_error_complete(self, groq_client):
        """Test complete error analysis"""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {"retry-after": "30", "x-ratelimit-remaining-requests": "0"}

        result = {"error": "Rate limit exceeded"}

        error_msg, is_retryable, rate_limit_info = groq_client._analyze_response_error(mock_response, result)

        assert "HTTP Status Code: 429" in error_msg
        assert "Too Many Requests" in error_msg
        assert "Retry after: 30 seconds" in error_msg
        assert "API Error (error): Rate limit exceeded" in error_msg
        assert is_retryable is True
        assert rate_limit_info.retry_after == 30

    @patch.object(AccGPTChatGroq, "_make_api_request")
    def test_generate_success_first_model(self, mock_make_api, groq_client, sample_messages):
        """Test successful generation with first model"""
        mock_result = ChatResult(generations=[ChatGeneration(message=AIMessage(content="Success"))])
        mock_make_api.return_value = mock_result

        result = groq_client._generate(sample_messages)

        assert result == mock_result
        mock_make_api.assert_called_once_with(sample_messages, "test-model")

    @patch.object(AccGPTChatGroq, "_make_api_request")
    def test_generate_fallback_success(self, mock_make_api, groq_client, sample_messages):
        """Test successful generation with fallback model"""
        groq_client.fallback_models = ["fallback-model-1", "fallback-model-2"]

        # First model fails, second succeeds
        mock_result = ChatResult(generations=[ChatGeneration(message=AIMessage(content="Fallback success"))])
        mock_make_api.side_effect = [GroqAPIError("First model failed", is_retryable=False), mock_result]

        result = groq_client._generate(sample_messages)

        assert result == mock_result
        assert mock_make_api.call_count == 2

    @patch.object(AccGPTChatGroq, "_make_api_request")
    def test_generate_all_models_fail(self, mock_make_api, groq_client, sample_messages):
        """Test generation when all models fail"""
        groq_client.fallback_models = ["fallback-model-1"]

        mock_make_api.side_effect = [
            GroqAPIError("First model failed", is_retryable=False),
            GroqAPIError("Second model failed", is_retryable=False),
        ]

        with pytest.raises(GroqAPIError) as exc_info:
            groq_client._generate(sample_messages)

        assert "Second model failed" in str(exc_info.value)
        assert mock_make_api.call_count == 2

    def test_message_formatting(self, groq_client):
        """Test that messages are formatted correctly for API"""
        messages = [
            SystemMessage(content="System prompt"),
            HumanMessage(content="User question"),
            AIMessage(content="AI response"),
        ]

        with patch.object(groq_client, "_make_api_request") as mock_api:
            mock_api.return_value = ChatResult(generations=[ChatGeneration(message=AIMessage(content="Test"))])

            groq_client._generate(messages)

            # Check the messages passed to API
            call_args = mock_api.call_args[0]
            passed_messages = call_args[0]

            assert len(passed_messages) == 3
            assert isinstance(passed_messages[0], SystemMessage)
            assert isinstance(passed_messages[1], HumanMessage)
            assert isinstance(passed_messages[2], AIMessage)


class TestIntegration:
    """Integration tests that test the full flow"""

    @pytest.fixture
    def groq_client_with_retries(self):
        """Create a client configured for retries"""
        return AccGPTChatGroq(
            base_url="http://test-server.com",
            api_key="test-api-key",
            model_name="test-model",
            fallback_models=["fallback-1", "fallback-2"],
            retry_config=RetryConfig(
                max_retries=2,
                base_delay=0.1,  # Fast for testing
                max_delay=1.0,
                jitter=False,  # Predictable for testing
            ),
        )

    @patch("chATLAS_Chains.llm.groq.requests.post")
    @patch("chATLAS_Chains.llm.groq.time.sleep")
    def test_full_retry_and_fallback_flow(self, mock_sleep, mock_post, groq_client_with_retries):
        """Test the complete retry and fallback flow"""
        # Model 1: Retryable error, then success
        mock_response_retry = Mock()
        mock_response_retry.status_code = 503
        mock_response_retry.json.return_value = {"error": "Service unavailable"}
        mock_response_retry.headers = {}

        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {"choices": [{"message": {"content": "Final success"}}]}
        mock_response_success.headers = {}

        # Sequence: fail, retry and succeed
        mock_post.side_effect = [mock_response_retry, mock_response_success]

        messages = [HumanMessage(content="Test question")]
        result = groq_client_with_retries.invoke(messages)

        assert result.content == "Final success"
        assert mock_post.call_count == 2
        assert mock_sleep.call_count == 1

    @patch("chATLAS_Chains.llm.groq.requests.post")
    def test_rate_limit_handling_integration(self, mock_post, groq_client_with_retries):
        """Test rate limit handling in integration"""
        # Return rate limit error
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.json.return_value = {"error": "Rate limit exceeded"}
        mock_response.headers = {
            "retry-after": "1",
            "x-ratelimit-remaining-requests": "0",
            "x-ratelimit-limit-requests": "1000",
        }
        mock_post.return_value = mock_response

        messages = [HumanMessage(content="Test question")]

        with pytest.raises(GroqAPIError) as exc_info:
            groq_client_with_retries.invoke(messages)

        exc = cast(GroqAPIError, exc_info.value)  # fix type checking
        assert exc.status_code == 429
        rate_info = cast(RateLimitInfo, exc.rate_limit_info)
        assert rate_info.retry_after == 1


class TestEdgeCases:
    """Test edge cases and error conditions"""

    def test_empty_messages(self):
        """Test behavior with empty message list"""
        client = AccGPTChatGroq(base_url="http://test-server.com", api_key="test-api-key", model_name="test-model")

        with patch.object(client, "_make_api_request") as mock_api:
            mock_api.return_value = ChatResult(generations=[ChatGeneration(message=AIMessage(content="Test"))])

            client._generate([])
            mock_api.assert_called_once_with([], "test-model")

    def test_very_long_content(self):
        """Test handling of very long message content"""
        client = AccGPTChatGroq(base_url="http://test-server.com", api_key="test-api-key", model_name="test-model")

        long_content = "x" * 10000  # Very long string
        messages = [HumanMessage(content=long_content)]

        with patch.object(client, "_make_api_request") as mock_api:
            mock_api.return_value = ChatResult(generations=[ChatGeneration(message=AIMessage(content="Test"))])

            client._generate(messages)

            # Verify the long content was passed through
            call_args = mock_api.call_args[0]
            assert call_args[0][0].content == long_content

    def test_unicode_content(self):
        """Test handling of unicode content"""
        client = AccGPTChatGroq(base_url="http://test-server.com", api_key="test-api-key", model_name="test-model")

        unicode_content = "Hello 世界! 🌍 Café naïve résumé"
        messages = [HumanMessage(content=unicode_content)]

        with patch.object(client, "_make_api_request") as mock_api:
            mock_api.return_value = ChatResult(generations=[ChatGeneration(message=AIMessage(content="Test"))])

            client._generate(messages)

            call_args = mock_api.call_args[0]
            assert call_args[0][0].content == unicode_content

    def test_extreme_retry_configuration(self):
        """Test extreme retry configuration values"""
        client = AccGPTChatGroq(
            base_url="http://test-server.com",
            api_key="test-api-key",
            model_name="test-model",
            retry_config=RetryConfig(
                max_retries=100, base_delay=0.001, max_delay=1.0, exponential_base=1.1, jitter=False
            ),
        )

        # Should handle extreme values gracefully
        delay = client._calculate_delay(50)
        assert client.retry_config is not None
        assert 0 <= delay <= client.retry_config.max_delay

    @patch("chATLAS_Chains.llm.groq.requests.post")
    def test_zero_retry_configuration(self, mock_post):
        """Test with zero retries"""
        client = AccGPTChatGroq(
            base_url="http://test-server.com",
            api_key="test-api-key",
            model_name="test-model",
            retry_config=RetryConfig(max_retries=0),
        )

        mock_response = Mock()
        mock_response.status_code = 503
        mock_response.json.return_value = {"error": "Service unavailable"}
        mock_response.headers = {}
        mock_post.return_value = mock_response

        messages = [HumanMessage(content="Test")]

        with pytest.raises(GroqAPIError):
            client._make_api_request(messages, "test-model")

        # Should only make one call (no retries)
        assert mock_post.call_count == 1


class TestLogging:
    """Test logging behavior"""

    def test_debug_logging_enabled(self):
        """Test that debug logging works when enabled"""
        client = AccGPTChatGroq(
            base_url="http://test-server.com", api_key="test-api-key", model_name="test-model", debug=True
        )

        with patch("chATLAS_Chains.llm.groq.logger") as mock_logger:
            info = RateLimitInfo(requests_remaining=100, requests_limit=1000)
            client._log_rate_limit_info(info)

            assert mock_logger.debug.call_count > 0

    def test_debug_logging_disabled(self):
        """Test that debug logging is disabled when debug=False"""
        client = AccGPTChatGroq(
            base_url="http://test-server.com", api_key="test-api-key", model_name="test-model", debug=False
        )

        # When debug=False, _log_rate_limit_info should return early and not call logger
        info = RateLimitInfo(requests_remaining=100, requests_limit=1000)
        client._log_rate_limit_info(info)  # Should not raise any errors


# Fixture for pytest configuration
@pytest.fixture(autouse=True)
def setup_logging():
    """Setup logging for tests"""
    logging.basicConfig(level=logging.DEBUG)

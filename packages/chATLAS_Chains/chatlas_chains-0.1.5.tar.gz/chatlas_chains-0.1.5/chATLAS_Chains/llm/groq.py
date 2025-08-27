import json
import logging
import os
import random
import re
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Optional

import requests
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from pydantic import BaseModel, Field, SecretStr
from requests.exceptions import ConnectionError, RequestException, Timeout

logger = logging.getLogger(__name__)


@dataclass
class RateLimitInfo:
    """Store rate limit information from Groq API headers"""

    requests_limit: int | None = None
    tokens_limit: int | None = None
    requests_remaining: int | None = None
    tokens_remaining: int | None = None
    requests_reset_time: float | None = None  # seconds until reset
    tokens_reset_time: float | None = None  # seconds until reset
    retry_after: int | None = None  # seconds to wait before retry


@dataclass
class RetryConfig:
    """Configuration for retry behavior

    max_retries: Maximum number of retry attempts.
    base_delay: Base delay in seconds for exponential backoff.
    max_delay: Maximum delay before retry in seconds.
    exponential_base: Base for exponential backoff calculation.
    jitter: Whether to add random jitter to the delay to prevent thundering herd.
    respect_rate_limits: Whether to automatically handle rate limits by waiting for reset times.
    """

    max_retries: int = 0
    base_delay: float = 1.0  # (seconds)
    max_delay: float = 60.0
    exponential_base: float = 2.0  # For exponential backoff
    jitter: bool = True  # Add random jitter to prevent thundering herd
    respect_rate_limits: bool = True  # Whether to automatically handle rate limits


class GroqAPIError(Exception):
    """Custom exception for Groq API errors"""

    def __init__(
        self,
        message: str,
        response_data: dict[Any, Any] | None = None,
        status_code: int | None = None,
        is_retryable: bool = False,
        rate_limit_info: RateLimitInfo | None = None,
    ):
        super().__init__(message)
        self.response_data = response_data
        self.status_code = status_code
        self.is_retryable = is_retryable
        self.rate_limit_info = rate_limit_info


class AccGPTChatGroq(BaseChatModel, BaseModel):
    """
    A custom LangChain chat model for interacting with the Groq API from AccGPT via their provided proxy server.
    This model supports rate limit awareness, retries, and fallbacks to alternative models in case of failures.

    :param base_url: The URL of the Groq API server.
    :type base_url: SecretStr

    :param api_key: The API key for authenticating with the Groq API.
    :type api_key: SecretStr

    :param model_name: The name of the model to use
    :type model_name: str

    :param temperature: The temperature of the model, default is None, which uses the model's default value.
    :type temperature: float | None

    :param max_tokens: The maximum number of tokens to generate in the response, default is None, which uses the model's default value.
    :type max_tokens: int | None

    :param timeout: The timeout for API requests in seconds, default is 30.
    :type timeout: int

    :param debug: If True, enables debug logging for API requests and responses.
    :type debug: bool

    :param retry_config: Configuration for retry behavior, including max retries, base delay, and rate limit handling.
    :type retry_config: RetryConfig

    :param fallback_models: List of alternative model names to try if the primary model fails.
    :type fallback_models: list[str]


    Example:

        .. code-block:: python
            api_key = os.getenv("CHATLAS_GROQ_KEY")
            base_url = os.getenv("CHATLAS_GROQ_BASE_URL")

            model_name = "llama-3.1-8b-instant"

            llm = AccGPTChatGroq(
                base_url=base_url,
                api_key=api_key,
                model_name=model_name,
                max_tokens=150,
                temperature=0.1,
            )

            result = llm.invoke("what is the Higgs boson?")


    TODO: To implement streaming, custom _stream method required, see:
    https://python.langchain.com/api_reference/core/language_models/langchain_core.language_models.chat_models.BaseChatModel.html
    https://python.langchain.com/docs/how_to/custom_chat_model/
    """

    base_url: SecretStr
    api_key: SecretStr
    model_name: str
    temperature: float | None = None
    max_tokens: int | None = None
    timeout: int = 30
    debug: bool = False
    retry_config: RetryConfig | None = None
    fallback_models: list[str] | None = None

    def __init__(self, **data):
        super().__init__(**data)
        if self.retry_config is None:
            self.retry_config = RetryConfig()

        if self.fallback_models is None:
            self.fallback_models = []

    def _parse_time_duration(self, duration_str: str) -> float:
        """Parse Groq time duration format (e.g., '2m59.56s', '7.66s') to seconds"""
        try:
            # Remove any whitespace
            duration_str = duration_str.strip()

            # Pattern to match formats like '2m59.56s', '7.66s', '1h30m45s'
            pattern = r"(?:(\d+)h)?(?:(\d+)m)?(?:(\d+(?:\.\d+)?)s)?"
            match = re.match(pattern, duration_str)

            if not match:
                logger.debug(f"Could not parse duration: {duration_str}")
                return 0.0

            hours, minutes, seconds = match.groups()

            total_seconds = 0.0
            if hours:
                total_seconds += int(hours) * 3600
            if minutes:
                total_seconds += int(minutes) * 60
            if seconds:
                total_seconds += float(seconds)

            return total_seconds

        except Exception as e:
            logger.debug(f"Error parsing duration '{duration_str}': {e}")
            return 0.0

    def _parse_rate_limit_headers(self, headers: dict[str, str]) -> RateLimitInfo:
        """Parse rate limit information from response headers"""
        rate_limit_info = RateLimitInfo()

        try:
            # Parse retry-after header
            if "retry-after" in headers:
                rate_limit_info.retry_after = int(headers["retry-after"])

            # Parse request limits
            if "x-ratelimit-limit-requests" in headers:
                rate_limit_info.requests_limit = int(headers["x-ratelimit-limit-requests"])

            if "x-ratelimit-remaining-requests" in headers:
                rate_limit_info.requests_remaining = int(headers["x-ratelimit-remaining-requests"])

            if "x-ratelimit-reset-requests" in headers:
                rate_limit_info.requests_reset_time = self._parse_time_duration(headers["x-ratelimit-reset-requests"])

            # Parse token limits
            if "x-ratelimit-limit-tokens" in headers:
                rate_limit_info.tokens_limit = int(headers["x-ratelimit-limit-tokens"])

            if "x-ratelimit-remaining-tokens" in headers:
                rate_limit_info.tokens_remaining = int(headers["x-ratelimit-remaining-tokens"])

            if "x-ratelimit-reset-tokens" in headers:
                rate_limit_info.tokens_reset_time = self._parse_time_duration(headers["x-ratelimit-reset-tokens"])

        except (ValueError, KeyError) as e:
            logger.debug(f"Error parsing rate limit headers: {e}")

        return rate_limit_info

    def _log_rate_limit_info(self, rate_limit_info: RateLimitInfo):
        """Log rate limit information for debugging"""
        if not self.debug:
            return

        logger.debug("Rate limit information:")
        if rate_limit_info.requests_remaining is not None and rate_limit_info.requests_limit is not None:
            percentage = (rate_limit_info.requests_remaining / rate_limit_info.requests_limit) * 100
            logger.debug(
                f"  Requests: {rate_limit_info.requests_remaining}/{rate_limit_info.requests_limit} ({percentage:.1f}% remaining)"
            )
            if rate_limit_info.requests_reset_time:
                logger.debug(f"  Requests reset in: {rate_limit_info.requests_reset_time:.1f}s")

        if rate_limit_info.tokens_remaining is not None and rate_limit_info.tokens_limit is not None:
            percentage = (rate_limit_info.tokens_remaining / rate_limit_info.tokens_limit) * 100
            logger.debug(
                f"  Tokens: {rate_limit_info.tokens_remaining}/{rate_limit_info.tokens_limit} ({percentage:.1f}% remaining)"
            )
            if rate_limit_info.tokens_reset_time:
                logger.debug(f"  Tokens reset in: {rate_limit_info.tokens_reset_time:.1f}s")

        if rate_limit_info.retry_after:
            logger.debug(f"  Retry after: {rate_limit_info.retry_after}s")

    def _calculate_rate_limit_delay(self, rate_limit_info: RateLimitInfo) -> float:
        """Calculate appropriate delay based on rate limit information"""
        if not self.retry_config.respect_rate_limits:
            return 0.0

        delays = []

        # If retry-after header is present, respect it
        if rate_limit_info.retry_after:
            delays.append(rate_limit_info.retry_after)

        # Check if we're close to token rate limit
        if (
            rate_limit_info.tokens_remaining is not None
            and rate_limit_info.tokens_limit is not None
            and rate_limit_info.tokens_reset_time is not None
        ):
            # If we have less than 10% tokens remaining, wait for reset
            tokens_percentage = rate_limit_info.tokens_remaining / rate_limit_info.tokens_limit
            if tokens_percentage < 0.1:
                logger.warning(f"Low token availability ({tokens_percentage:.1%}), waiting for reset")
                delays.append(rate_limit_info.tokens_reset_time + 1)  # Add 1 second buffer

        # Check if we're close to request rate limit
        if (
            rate_limit_info.requests_remaining is not None
            and rate_limit_info.requests_limit is not None
            and rate_limit_info.requests_reset_time is not None
        ):
            # If we have less than 5% requests remaining, wait for reset
            requests_percentage = rate_limit_info.requests_remaining / rate_limit_info.requests_limit
            if requests_percentage < 0.05:
                logger.warning(f"Low request availability ({requests_percentage:.1%}), waiting for reset")
                delays.append(rate_limit_info.requests_reset_time + 1)  # Add 1 second buffer

        # Return the minimum necessary delay
        if delays:
            delay = min(delays)
            return min(delay, self.retry_config.max_delay)  # Cap at max_delay

        return 0.0

    def _is_retryable_error(self, status_code: int, error_message: str, rate_limit_info: RateLimitInfo) -> bool:
        """Determine if an error is retryable"""
        # Rate limit errors are always retryable
        if status_code == 429:
            return True

        # Retryable status codes
        retryable_codes = {
            500,  # Internal Server Error
            502,  # Bad Gateway
            503,  # Service Unavailable
            504,  # Gateway Timeout
        }

        if status_code in retryable_codes:
            return True

        # Check for specific error patterns that might be retryable
        retryable_patterns = ["service unavailable", "temporarily unavailable", "timeout", "rate limit", "server error"]

        error_lower = error_message.lower()
        return any(pattern in error_lower for pattern in retryable_patterns)

    def _calculate_delay(self, attempt: int, rate_limit_info: RateLimitInfo | None = None) -> float:
        """Calculate delay for retry with exponential backoff, jitter, and rate limit awareness"""
        # Start with rate limit delay if available
        rate_limit_delay = 0.0
        if rate_limit_info:
            rate_limit_delay = self._calculate_rate_limit_delay(rate_limit_info)

        # Calculate exponential backoff delay
        exponential_delay = min(
            self.retry_config.base_delay * (self.retry_config.exponential_base**attempt), self.retry_config.max_delay
        )

        # Use the maximum of rate limit delay and exponential backoff
        delay = max(rate_limit_delay, exponential_delay)

        # Add jitter only to exponential component to avoid interfering with rate limit timing
        if self.retry_config.jitter and rate_limit_delay == 0:
            jitter = exponential_delay * 0.25 * (2 * random.random() - 1)
            delay += jitter

        return max(delay, 0)

    def _analyze_response_error(
        self, response: requests.Response, result: dict[Any, Any]
    ) -> tuple[str, bool, RateLimitInfo]:
        """Analyze the response and provide detailed error information"""
        error_details = []

        # Parse rate limit information
        rate_limit_info = self._parse_rate_limit_headers(response.headers)

        # Check HTTP status code
        if response.status_code != 200:
            error_details.append(f"HTTP Status Code: {response.status_code}")

        # Common HTTP status code meanings
        status_meanings = {
            400: "Bad Request - Invalid model name or parameters",
            401: "Unauthorized - Invalid or missing API key",
            403: "Forbidden - Access denied or insufficient permissions",
            404: "Not Found - Model not available on Groq API",
            429: "Too Many Requests - Rate limit exceeded",
            500: "Internal Server Error - Server-side issue",
            502: "Bad Gateway - Proxy server error",
            503: "Service Unavailable - Server temporarily unavailable",
            504: "Gateway Timeout - Request timeout",
        }

        if response.status_code in status_meanings:
            error_details.append(f"Status Meaning: {status_meanings[response.status_code]}")

        # Special handling for rate limit errors
        if response.status_code == 429:
            if rate_limit_info.retry_after:
                error_details.append(f"Retry after: {rate_limit_info.retry_after} seconds")
            self._log_rate_limit_info(rate_limit_info)

        # Check for error fields in response
        error_fields = ["error", "errors", "message", "detail", "error_message"]
        for field in error_fields:
            if field in result:
                error_msg = str(result[field])
                error_details.append(f"API Error ({field}): {error_msg}")

        is_retryable = self._is_retryable_error(response.status_code, " ".join(error_details), rate_limit_info)

        return " | ".join(error_details) if error_details else "Unknown error", is_retryable, rate_limit_info

    def _make_api_request(self, messages: list[BaseMessage], model_name: str) -> ChatResult:
        """Make API request with retry logic and rate limit awareness"""
        formatted_messages = []

        for message in messages:
            if isinstance(message, SystemMessage):
                formatted_messages.append({"role": "system", "content": message.content})
            elif isinstance(message, HumanMessage):
                formatted_messages.append({"role": "user", "content": message.content})
            elif isinstance(message, AIMessage):
                formatted_messages.append({"role": "assistant", "content": message.content})

        chat_payload = {"messages": formatted_messages, "model": model_name, "n": 1}

        if self.max_tokens is not None:
            chat_payload["max_tokens"] = self.max_tokens

        if self.temperature is not None:
            chat_payload["temperature"] = self.temperature

        url = f"{self.base_url.get_secret_value()}/chat"
        headers = {"X-API-Key": self.api_key.get_secret_value()}

        last_exception = None

        for attempt in range(self.retry_config.max_retries + 1):
            try:
                if attempt > 0:
                    # Use rate limit aware delay calculation
                    rate_limit_info = getattr(last_exception, "rate_limit_info", None) if last_exception else None
                    delay = self._calculate_delay(attempt - 1, rate_limit_info)

                    if delay > 0:
                        logger.info(
                            f"Retry attempt {attempt + 1}/{self.retry_config.max_retries + 1} for model {model_name} after {delay:.2f}s delay"
                        )
                        if rate_limit_info and (rate_limit_info.retry_after or delay > 10):
                            logger.warning("Waiting due to rate limit constraints...")
                        time.sleep(delay)

                logger.debug(f"Making API request to {url} (attempt {attempt + 1})")
                start_time = time.time()

                # print(f"chat_payload: {json.dumps(chat_payload, indent=2)}")
                # print(f"headers: {headers}")

                response = requests.post(url, json=chat_payload, headers=headers, timeout=self.timeout)

                request_duration = time.time() - start_time
                logger.debug(f"Request completed in {request_duration:.2f} seconds")

                # Parse rate limit info from successful requests too
                rate_limit_info = self._parse_rate_limit_headers(response.headers)
                self._log_rate_limit_info(rate_limit_info)

                # Try to parse JSON response
                try:
                    result = response.json()
                except json.JSONDecodeError as e:
                    error_msg = f"Failed to parse JSON response: {e!s}"
                    logger.error(error_msg)
                    logger.error(f"Raw response content (first 500 chars): {response.text[:500]}")
                    raise GroqAPIError(error_msg, status_code=response.status_code, is_retryable=True)

                # Check if request was successful
                if response.status_code != 200:
                    error_details, is_retryable, rate_limit_info = self._analyze_response_error(response, result)
                    error_msg = f"API request failed with status {response.status_code}: {error_details}"
                    logger.error(error_msg)

                    if not is_retryable or attempt == self.retry_config.max_retries:
                        raise GroqAPIError(
                            error_msg,
                            response_data=result,
                            status_code=response.status_code,
                            is_retryable=is_retryable,
                            rate_limit_info=rate_limit_info,
                        )
                    else:
                        last_exception = GroqAPIError(
                            error_msg,
                            response_data=result,
                            status_code=response.status_code,
                            is_retryable=is_retryable,
                            rate_limit_info=rate_limit_info,
                        )
                        logger.info("Error is retryable, will retry...")
                        continue

                # Validate response structure
                if not isinstance(result, dict):
                    error_msg = f"Expected dict response, got {type(result)}"
                    raise GroqAPIError(error_msg, response_data=result, is_retryable=True)

                if "choices" not in result:
                    error_msg = "Response missing 'choices' field"
                    logger.error(error_msg)
                    logger.error(f"Available fields: {list(result.keys())}")
                    raise GroqAPIError(error_msg, response_data=result, is_retryable=True)

                if not isinstance(result["choices"], list) or len(result["choices"]) == 0:
                    error_msg = "Invalid 'choices' field: expected non-empty list"
                    raise GroqAPIError(error_msg, response_data=result, is_retryable=True)

                choice = result["choices"][0]
                if not isinstance(choice, dict) or "message" not in choice:
                    error_msg = "Invalid choice structure: expected dict with 'message' field"
                    raise GroqAPIError(error_msg, response_data=result, is_retryable=True)

                message = choice["message"]
                if not isinstance(message, dict) or "content" not in message:
                    error_msg = "Invalid message structure: expected dict with 'content' field"
                    raise GroqAPIError(error_msg, response_data=result, is_retryable=True)

                if choice.get("finish_reason") == "length":
                    logger.warning("Model ran out of tokens before completing response, increase max_tokens")

                content = message["content"]
                logger.info(f"Successfully extracted content with {len(content)} characters from model {model_name}")

                return ChatResult(generations=[ChatGeneration(message=AIMessage(content=content))])

            except (
                Timeout,
                ConnectionError,
                RequestException,
            ) as e:
                error_msg = f"Network error: {e!s}"
                logger.error(error_msg)
                last_exception = GroqAPIError(error_msg, is_retryable=True)

                if attempt == self.retry_config.max_retries:
                    raise last_exception
                else:
                    logger.info("Network error is retryable, will retry...")
                    continue

            except GroqAPIError as e:
                last_exception = e
                if not e.is_retryable or attempt == self.retry_config.max_retries:
                    raise e
                else:
                    logger.info("API error is retryable, will retry...")
                    continue

        # If we get here, all retries failed
        if last_exception:
            raise last_exception
        else:
            raise GroqAPIError("All retry attempts failed")

    def _generate(self, messages: list[BaseMessage], **kwargs) -> ChatResult | None:
        """
        Generate response with fallback to alternative models if primary fails
        """
        models_to_try = [self.model_name, *self.fallback_models]

        for i, model in enumerate(models_to_try):
            try:
                logger.info(f"Trying model {i + 1}/{len(models_to_try)}: {model}")
                return self._make_api_request(messages, model)

            except GroqAPIError as e:
                logger.error(f"Model {model} failed: {e!s}")

                # If this is the last model, re-raise the exception
                if i == len(models_to_try) - 1:
                    logger.error(f"All models failed. Last error: {e!s}")
                    raise e

                # If error is not retryable (like 404 Not Found), try next model immediately
                if not e.is_retryable:
                    logger.info("Error not retryable, trying next model...")
                    continue
                else:
                    logger.info("Retryable error occurred, trying next model...")
                    continue

    def _stream(self, **kwargs):
        raise NotImplementedError("AccGPTChatGroqRateLimitAware does not support streaming yet.")

    @property
    def _llm_type(self) -> str:
        return self.model_name


# Example usage with rate limit aware error handling
if __name__ == "__main__":
    # Define reliable fallback models based on your test results
    RELIABLE_MODELS = ["gemma2-9b-it", "llama-3.1-8b-instant", "llama3-8b-8192", "compound-beta-mini", "allam-2-7b"]

    print(f"Starting rate limit aware AccGPTChatGroq test at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC")

    api_key = os.getenv("CHATLAS_GROQ_KEY")
    if not api_key or not api_key.strip():
        raise ValueError("CHATLAS_GROQ_KEY not set in environment")
    api_key = api_key.strip()

    base_url = os.getenv("CHATLAS_GROQ_BASE_URL")
    base_url = "http://localhost:3000"
    if not base_url or not base_url.strip():
        raise ValueError("CHATLAS_GROQ_BASE_URL not set in environment")
    base_url = base_url.strip()

    # Test with rate limit aware configuration
    llm = AccGPTChatGroq(
        base_url=base_url,
        api_key=api_key,
        model_name="deepseek-r1-distill-llama-70b",
        fallback_models=RELIABLE_MODELS[1:3],  # Use reliable models as fallbacks
        temperature=0.1,
        max_tokens=150,
        debug=True,
        retry_config=RetryConfig(
            max_retries=3,
            base_delay=1.0,
            max_delay=300.0,  # Allow up to 5 minutes for rate limit waits
            respect_rate_limits=True,
        ),
    )

    try:
        result = llm.invoke("what is the Higgs boson?")
        print(f"Final result type: {type(result)}")
        print(f"Final result: {result}")
    except Exception as e:
        logger.error(f"All fallbacks failed: {e!s}")
        import traceback

        traceback.print_exc()

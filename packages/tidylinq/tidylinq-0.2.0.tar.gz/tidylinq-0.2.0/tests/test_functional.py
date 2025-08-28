from __future__ import annotations

import time
from unittest.mock import Mock, patch

import pytest
from pydantic import BaseModel

from tidylinq.functional import completion_with_schema, retry


class TestRetry:
    def test_retry_success_on_first_attempt(self):
        """Function succeeds on first attempt."""
        mock_func = Mock(return_value="success")
        wrapped = retry(mock_func, retries=3)

        result = wrapped("arg", kwarg="value")

        assert result == "success"
        mock_func.assert_called_once_with("arg", kwarg="value")

    def test_retry_success_after_failures(self):
        """Function succeeds after some failures."""
        mock_func = Mock(side_effect=[ValueError("fail"), ValueError("fail"), "success"])
        wrapped = retry(mock_func, retries=3)

        result = wrapped()

        assert result == "success"
        assert mock_func.call_count == 3

    def test_retry_exhausts_attempts(self):
        """Function fails on all attempts."""
        mock_func = Mock(side_effect=ValueError("always fails"))
        wrapped = retry(mock_func, retries=2)

        with pytest.raises(ValueError, match="always fails"):
            wrapped()

        assert mock_func.call_count == 2

    def test_retry_with_backoff(self):
        """Backoff parameter causes sleep between retries."""
        mock_func = Mock(side_effect=[ValueError("fail"), "success"])

        start_time = time.time()
        wrapped = retry(mock_func, retries=3, backoff=0.1)
        result = wrapped()
        end_time = time.time()

        assert result == "success"
        assert mock_func.call_count == 2
        # Should have slept at least 0.1 seconds between attempts
        assert end_time - start_time >= 0.1

    def test_retry_no_backoff_when_zero(self):
        """No sleep when backoff is 0."""
        mock_func = Mock(side_effect=[ValueError("fail"), "success"])

        start_time = time.time()
        wrapped = retry(mock_func, retries=3, backoff=0.0)
        result = wrapped()
        end_time = time.time()

        assert result == "success"
        assert mock_func.call_count == 2
        # Should complete quickly without sleep
        assert end_time - start_time < 0.05

    def test_retry_preserves_function_metadata(self):
        """Wrapped function preserves original function metadata."""

        def original_func(x: int) -> str:
            """Original docstring."""
            return str(x)

        wrapped = retry(original_func)

        assert wrapped.__name__ == "original_func"
        assert wrapped.__doc__ == "Original docstring."

    def test_retry_with_different_exception_types(self):
        """Different exception types are handled correctly."""
        mock_func = Mock(side_effect=[KeyError("key"), ValueError("value"), "success"])
        wrapped = retry(mock_func, retries=4)

        result = wrapped()

        assert result == "success"
        assert mock_func.call_count == 3


class TestCompletionWithSchema:
    def test_completion_with_schema_success(self):
        """Successful completion with valid JSON response."""

        class TestModel(BaseModel):
            message: str
            count: int

        mock_response = Mock()
        mock_choice = Mock()
        mock_choice.message.content = '{"message": "hello", "count": 42}'
        mock_response.choices = [mock_choice]

        with patch("litellm.completion", return_value=mock_response) as mock_completion:
            result = completion_with_schema(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "test"}],
                response_schema=TestModel,
                temperature=0.5,
            )

        assert isinstance(result, TestModel)
        assert result.message == "hello"
        assert result.count == 42

        mock_completion.assert_called_once_with(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "test"}],
            response_format=TestModel,
            temperature=0.5,
        )

    def test_completion_with_schema_none_content(self):
        """Raises assertion error when response content is None."""

        class TestModel(BaseModel):
            message: str

        mock_response = Mock()
        mock_choice = Mock()
        mock_choice.message.content = None
        mock_response.choices = [mock_choice]

        with patch("litellm.completion", return_value=mock_response):
            with pytest.raises(AssertionError, match="Response content is None"):
                completion_with_schema(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "test"}],
                    response_schema=TestModel,
                )

    def test_completion_with_schema_invalid_json(self):
        """Raises validation error for invalid JSON."""

        class TestModel(BaseModel):
            message: str
            count: int

        mock_response = Mock()
        mock_choice = Mock()
        mock_choice.message.content = '{"message": "hello"}'  # Missing required field
        mock_response.choices = [mock_choice]

        with patch("litellm.completion", return_value=mock_response):
            with pytest.raises(ValueError):  # Pydantic validation error
                completion_with_schema(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "test"}],
                    response_schema=TestModel,
                )

from collections.abc import Callable
from functools import wraps
from time import sleep
from typing import TypeVar, cast

from pydantic import BaseModel

T = TypeVar("T")


def retry(f: Callable[..., T], retries: int = 3, backoff: float = 0.0) -> Callable[..., T]:
    """
    Decorator to retry a function call a specified number of times if it raises an exception.

    If `backoff` is greater than 0, it will sleep for the specified number of seconds
    between retries, with exponential backoff for repeated failures.

    :param f: The function to be retried.
    :param retries: The number of times to retry the function.
    :param backoff: Time in seconds to sleep between retries.
    :return: A wrapped function that retries on failure.
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        for attempt in range(retries):
            try:
                return f(*args, **kwargs)
            except Exception as e:
                if attempt == retries - 1:
                    raise e
                if backoff > 0:
                    sleep(backoff * (2**attempt))
        raise RuntimeError("Can't happen.")

    return wrapper


V = TypeVar("V", bound=type[BaseModel])


def completion_with_schema(
    model: str,
    messages: list[dict[str, str]],
    response_schema: V,
    **kwargs,
) -> V:
    """Wrapper for litellm.completion with Pydantic schema response format.

    :param model: The model to use for completion.
    :param messages: The messages to send to the model.
    :param response_schema: The Pydantic schema to validate the response against.
    :param kwargs: Additional arguments for litellm.completion.
    :return: The validated response as an instance of response_schema.
    """
    import litellm

    response = litellm.completion(  # type: ignore
        model=model,
        messages=messages,
        response_format=response_schema,
        **kwargs,
    )

    message_content = cast(litellm.Choices, response.choices)[0].message.content  # type: ignore
    assert message_content is not None, "Response content is None"
    return response_schema.model_validate_json(message_content)  # type: ignore

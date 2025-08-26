from collections.abc import Iterator

from any_llm import completion
from any_llm.provider import ProviderFactory
from any_llm.types.completion import ChatCompletion, ChatCompletionChunk
from halo import Halo

from .logging import logger


def get_llm_response(prompt: str, model: str, api_base: str) -> str | None:
    """Get a response from the LLM.

    This function sends a prompt to the specified LLM model, at the given API base URL, and returns the response.
    The response of the LLM should adhere to OpenAI's API specifications.
    Then, the function returns the LLM's response as a string, or None if no response is received.

    Args:
        prompt (str): The prompt to send to the LLM.
        model (str): The LLM model to use.
        api_base (str): The provider's API base URL.

    Returns:
        str: The LLM's response.

    Raises:
        ConnectionError: If the connection to the LLM fails.
        RuntimeError: The LLM response should be a valid ChatCompletion object. Otherwise, an error is raised.
    """
    provider, _ = ProviderFactory.split_model_provider(model)

    spinner = Halo(text="🤖 Thinking...", spinner="dots", color="cyan")

    spinner.start()

    try:
        response: ChatCompletion | Iterator[ChatCompletionChunk] = completion(
            model=model, messages=[{"role": "user", "content": prompt}], api_base=api_base
        )
    except ConnectionError as e:
        spinner.stop()
        error_message = f"Failed to connect to {provider.capitalize()} at {api_base}. Please check your `.env` file."
        logger.error(error_message)
        raise ConnectionError(error_message) from e
    except Exception as e:
        spinner.stop()
        logger.error(f"An error occurred while communicating with {provider.capitalize()}: {e}")
        raise

    if isinstance(response, ChatCompletion):
        spinner.stop()
        return response.choices[0].message.content
    else:
        spinner.stop()
        logger.error("Response type not supported")
        raise RuntimeError("Response type not supported")

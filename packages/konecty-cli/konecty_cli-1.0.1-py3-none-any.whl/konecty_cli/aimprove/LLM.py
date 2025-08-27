from openai import OpenAI

from ..config.types import ConfigAi


def get_llm(config: ConfigAi):
    """Get the LLM for the given config."""
    match config.provider:
        case "openai":
            return OpenAI(api_key=config.api_key)
        case _:
            raise ValueError(f"Invalid provider: {config.provider}")

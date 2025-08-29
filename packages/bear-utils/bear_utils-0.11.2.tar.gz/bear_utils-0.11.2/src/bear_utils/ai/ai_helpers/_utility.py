from pydantic import BaseModel

from ._config import AIEndpointConfig
from ._parsers import ModularAIEndpoint
from ._types import BaseModelParser


def create_endpoint[T_Response: BaseModel](
    config: AIEndpointConfig,
    response_model: type[T_Response],
) -> ModularAIEndpoint[T_Response]:
    """Create a ModularAIEndpoint with the specified configuration and response parser."""
    return ModularAIEndpoint(config=config, response_parser=BaseModelParser(response_model))

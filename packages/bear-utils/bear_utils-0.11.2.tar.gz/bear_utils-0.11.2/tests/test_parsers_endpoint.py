import json

import httpx
from pydantic import BaseModel, SecretStr, field_validator
import pytest
from bear_epoch_time import EpochTimestamp
from bear_utils.ai.ai_helpers._config import AIEndpointConfig, AIPlatform, AISetup, AnyHttpUrl, EnvMode
from bear_utils.ai import BaseModelParser
from bear_utils.ai.ai_helpers._parsers import ModularAIEndpoint
from bear_utils.constants import HTTPStatusCode


def make_client(result: httpx.Response | Exception):
    class MockClient:
        def __init__(self, *args, **kwargs) -> None:
            pass

        async def __aenter__(self) -> "MockClient":  # type: ignore[override]
            return self

        async def __aexit__(self, exc_type, exc, tb) -> None:  # type: ignore[override]
            return None

        async def post(self, *args, **kwargs) -> httpx.Response:
            if isinstance(result, Exception):
                raise result
            return result

    return MockClient


@pytest.fixture
def mock_session_id() -> str:
    return EpochTimestamp.now().to_string()


# Test models
class MockResponse(BaseModel):
    """Test response model."""

    foo: str = ""
    bar: int = 0

    @field_validator("foo", mode="before")
    @classmethod
    def uppercase_foo(cls, v: str) -> str:
        """Transform foo to uppercase."""
        return v.upper() if v else ""


class SimpleResponse(BaseModel):
    """Simple response for error cases."""

    error: str = "Failed to parse response"


@pytest.mark.asyncio
async def test_basemodel_parser():
    """Test BaseModelParser with Pydantic model."""
    parser = BaseModelParser(MockResponse)

    # Test successful parsing
    good = {"output": json.dumps({"foo": "hello", "bar": 42})}
    parsed = await parser.parse(good)
    assert isinstance(parsed, MockResponse)
    assert parsed.foo == "HELLO"  # Field validator applied
    assert parsed.bar == 42

    # Test missing fields (should use defaults)
    partial = {"output": json.dumps({"foo": "world"})}
    parsed_partial = await parser.parse(partial)
    assert isinstance(parsed_partial, MockResponse)
    assert parsed_partial.foo == "WORLD"
    assert parsed_partial.bar == 0  # Default value

    # Test invalid JSON
    bad_json = {"output": "not json"}
    parsed_bad = await parser.parse(bad_json)
    assert isinstance(parsed_bad, MockResponse)
    assert parsed_bad.foo == ""  # Default
    assert parsed_bad.bar == 0  # Default


@pytest.fixture
def endpoint() -> ModularAIEndpoint[MockResponse]:
    ai_setup = AISetup(
        token=SecretStr("token"),
        model="gpt-4-1-nano",
        platform=AIPlatform.OPENAI,
        system_prompt="You are a helpful assistant.",
        url=AnyHttpUrl("https://example.com"),
    )

    config: AIEndpointConfig[MockResponse] = AIEndpointConfig(
        name="test",
        expected_type=MockResponse,
        ai=ai_setup,
        env=EnvMode.TEST,
        timeout=5,
    )
    parser = BaseModelParser(MockResponse)
    return ModularAIEndpoint(config, parser)


@pytest.mark.asyncio
async def test_modular_endpoint_success(
    monkeypatch: pytest.MonkeyPatch, endpoint: ModularAIEndpoint[MockResponse], mock_session_id: str
) -> None:
    response = httpx.Response(
        HTTPStatusCode.SERVER_OK,
        json={"output": json.dumps({"foo": "bar", "bar": 123})},
        request=httpx.Request("POST", endpoint.config.url),
    )
    monkeypatch.setattr("bear_utils.ai.ai_helpers._parsers.AsyncClient", make_client(response))

    result = await endpoint.send_message("hi", mock_session_id)
    assert isinstance(result, MockResponse)
    assert result.foo == "BAR"  # Field validator applied
    assert result.bar == 123


@pytest.mark.asyncio
async def test_modular_endpoint_http_error(
    monkeypatch: pytest.MonkeyPatch, endpoint: ModularAIEndpoint[MockResponse], mock_session_id: str
) -> None:
    response = httpx.Response(
        HTTPStatusCode.SERVER_ERROR,
        text="fail",
        request=httpx.Request("POST", endpoint.config.url),
    )
    monkeypatch.setattr("bear_utils.ai.ai_helpers._parsers.AsyncClient", make_client(response))
    result = await endpoint.send_message("hi", mock_session_id)
    assert isinstance(result, MockResponse)
    assert result.foo == ""  # Default value
    assert result.bar == 0  # Default value


@pytest.mark.asyncio
async def test_modular_endpoint_exception(
    monkeypatch: pytest.MonkeyPatch, endpoint: ModularAIEndpoint[MockResponse], mock_session_id: str
) -> None:
    monkeypatch.setattr(
        "bear_utils.ai.ai_helpers._parsers.AsyncClient",
        make_client(RuntimeError("boom")),
    )
    result = await endpoint.send_message("hi", mock_session_id)
    assert isinstance(result, MockResponse)
    assert result.foo == ""  # Default value
    assert result.bar == 0  # Default value

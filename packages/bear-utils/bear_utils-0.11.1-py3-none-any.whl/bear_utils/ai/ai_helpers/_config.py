from pydantic import AnyHttpUrl, BaseModel, SecretStr

from bear_utils.ai.ai_helpers._common import AIModel, AIPlatform, EnvironmentMode as EnvMode

DEFAULT_TIMEOUT = 20


class AISetup(BaseModel):
    """Basic setup for AI communication."""

    url: AnyHttpUrl = AnyHttpUrl("https://example.com")
    token: SecretStr = SecretStr("")
    model: AIModel | str = AIModel.GPT_4_1_NANO
    platform: AIPlatform = AIPlatform.OPENAI
    system_prompt: str | None = None


class AIEndpointConfig[T: BaseModel](BaseModel):
    """Configuration for AI endpoint communication."""

    name: str
    timeout: int = DEFAULT_TIMEOUT
    expected_type: type[T]
    env: EnvMode = EnvMode.PROD
    ai: AISetup = AISetup()

    @property
    def url(self) -> str:
        """Get the URL based on the environment."""
        return str(self.ai.url)

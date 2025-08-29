from enum import Enum, StrEnum


class EnvironmentMode(Enum):
    """Enumeration of environment modes."""

    TEST = "test"
    PROD = "prod"


class AIPlatform(Enum):
    """Enumeration of AI platforms."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class AIModel(StrEnum):
    """Enumeration of AI models."""

    GPT_5 = "gpt-5"
    GPT_5_NANO = "gpt-5-nano"
    GPT_5_MINI = "gpt-5-mini"

    GPT_4_1 = "gpt-4.1"
    GPT_4_1_NANO = "gpt-4.1-nano"
    GPT_4_1_MINI = "gpt-4.1-mini"

    CLAUDE_SONNET_4 = "clade-sonnet-4"


OPENAI = AIPlatform.OPENAI
ANTHROPIC = AIPlatform.ANTHROPIC

GPT_5 = AIModel.GPT_5
GPT_5_NANO = AIModel.GPT_5_NANO
GPT_5_MINI = AIModel.GPT_5_MINI

GPT_4_1 = AIModel.GPT_4_1
GPT_4_1_NANO = AIModel.GPT_4_1_NANO
GPT_4_1_MINI = AIModel.GPT_4_1_MINI

CLAUDE_SONNET_4 = AIModel.CLAUDE_SONNET_4

TESTING_MODE = EnvironmentMode.TEST
PRODUCTION_MODE = EnvironmentMode.PROD

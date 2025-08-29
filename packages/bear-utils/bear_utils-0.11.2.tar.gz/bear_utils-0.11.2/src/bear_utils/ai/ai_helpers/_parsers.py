from __future__ import annotations

from httpx import AsyncClient, Response
from pydantic import BaseModel

from bear_utils.ai.ai_helpers._types import BaseEndpoint, ToServerJson


class ModularAIEndpoint[T_Response: BaseModel](BaseEndpoint[T_Response]):
    """Modular AI endpoint for flexible communication patterns."""

    async def send_message(self, message: str, session_id: str) -> T_Response:
        """Send a message to the AI endpoint with flexible response parsing."""
        server_json = ToServerJson(chat_model=self.ai.model, chat_input=message, session_id=session_id)
        async with AsyncClient(timeout=self.config.timeout) as client:
            try:
                response: Response = await self._post(client, server_json)
            except Exception:
                return self.response_parser.get_default_response()
        return await self.response_parser.parse(response.json())

"""Middlewares."""

from __future__ import annotations

__all__: tuple[str, ...] = ("APIKeyQueryMiddleware",)

from typing import TYPE_CHECKING

from pydantic import BaseModel, SecretStr

if TYPE_CHECKING:  # pragma: no cover
    from aiohttp import ClientHandlerType, ClientRequest, ClientResponse


class APIKeyQueryMiddleware(BaseModel):
    """Middleware to add API key to query parameters."""

    api_key: SecretStr

    async def __call__(
        self,
        req: ClientRequest,
        handler: ClientHandlerType,
    ) -> ClientResponse:
        """Add API key to query parameters."""
        req.url = req.url % {"apiKey": self.api_key.get_secret_value()}
        return await handler(req)

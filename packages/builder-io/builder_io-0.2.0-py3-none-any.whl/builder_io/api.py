"""Builder.io API."""

from __future__ import annotations

__all__: tuple[str, ...] = ("BuilderIOContent", "BuilderIOWrite")

from typing import TYPE_CHECKING, cast

from aiohttp import ClientSession
from pydantic import BaseModel, ConfigDict, Field, SecretStr
from yarl import URL

from builder_io.middlewares import APIKeyQueryMiddleware

if TYPE_CHECKING:  # pragma: no cover
    from types import TracebackType
    from typing import Self

    from builder_io.utils import JSON


class BuilderIOWrite(BaseModel):
    """Builder.io Write API client."""

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )

    api_key: SecretStr

    base_url: URL = URL("https://builder.io/api")

    raw_session: ClientSession | None = Field(default=None, init=False)

    @property
    def session(self) -> ClientSession:
        """Get the aiohttp session."""
        if self.raw_session is None:
            msg = (
                f"Session not initialized. "
                f"Use 'async with {self.__class__.__name__}(...) as builder_write:'"
            )
            raise RuntimeError(msg)
        return self.raw_session

    async def __aenter__(self) -> Self:
        """Enter the async context."""
        self.raw_session = ClientSession(
            headers={"Authorization": f"Bearer {self.api_key.get_secret_value()}"},
        )
        await self.session.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit the async context."""
        await self.session.__aexit__(exc_type, exc_val, exc_tb)
        self.raw_session = None

    @property
    def v1(self) -> URL:
        """Get the v1 API URL."""
        return self.base_url / "v1"

    @property
    def write(self) -> URL:
        """Get the write API URL."""
        return self.v1 / "write"

    async def create_content(
        self,
        model: str,
        content: JSON,
    ) -> JSON:
        """Create new content in Builder.io."""
        async with self.session.post(
            self.write / model,
            json=content,
        ) as resp:
            resp.raise_for_status()
            return cast("JSON", await resp.json())

    async def update_content(
        self,
        model: str,
        entry_id: str,
        content: JSON,
    ) -> JSON:
        """Update existing content in Builder.io."""
        async with self.session.patch(
            self.write / model / entry_id,
            json=content,
        ) as resp:
            resp.raise_for_status()
            return cast("JSON", await resp.json())


class BuilderIOContent(BaseModel):
    """Builder.io Content API client."""

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )

    api_key: SecretStr

    base_url: URL = URL("https://cdn.builder.io/api")

    raw_session: ClientSession | None = Field(default=None, init=False)

    @property
    def session(self) -> ClientSession:
        """Get the aiohttp session."""
        if self.raw_session is None:
            msg = (
                f"Session not initialized. "
                f"Use 'async with {self.__class__.__name__}(...) as builder_content:'"
            )
            raise RuntimeError(msg)
        return self.raw_session

    async def __aenter__(self) -> Self:
        """Enter the async context."""
        self.raw_session = ClientSession(
            middlewares=(APIKeyQueryMiddleware(api_key=self.api_key),),
        )
        await self.session.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit the async context."""
        await self.session.__aexit__(exc_type, exc_val, exc_tb)
        self.raw_session = None

    @property
    def v3(self) -> URL:
        """Get the v3 API URL."""
        return self.base_url / "v3"

    @property
    def content(self) -> URL:
        """Get the content API URL."""
        return self.v3 / "content"

    async def get_content(
        self,
        model: str,
        query: dict[str, str],
    ) -> JSON:
        """Get content from Builder.io."""
        async with self.session.get(self.content / model % query) as resp:
            resp.raise_for_status()
            return cast("JSON", await resp.json())

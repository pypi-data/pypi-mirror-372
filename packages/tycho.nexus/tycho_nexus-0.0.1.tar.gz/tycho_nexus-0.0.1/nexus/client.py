"""

The main client.

"""

from .requests import Requests
from typing import List, Callable, Type, TypeVar, Dict, Any
from .api_types.v1 import *
from .exceptions import *
from .models import *
import httpx

R = TypeVar("R")


class Nexus:
    """The main Nexus API client."""

    def __init__(
        self,
        nexus_key: str,
        _base_url: str = "https://api.tycho.team/nexus/v1",
        _rts_base_url: str = "wss://rts.tycho.team/nexus/v1",
    ):
        self._nexus_key = nexus_key
        self._requests = Requests(
            base_url=_base_url, headers={"X-Nexus-Key": nexus_key}
        )
        self._rts_base_url = _rts_base_url

    def _raise_error_code(self, response: Any):
        if not isinstance(response, Dict):
            raise NexusException("A malformed response was received.")

        error_code = response.get("code")
        if error_code is None:
            raise NexusException("No error was received.")

        exceptions: List[Callable[..., APIException]] = [
            UnknownDiscordUser,
            UnknownKey,
            UnknownDiscordAccount,
            UnknownRobloxAccount,
            InternalError,
            InvalidParameter,
            RateLimited,
        ]

        for _exception in exceptions:
            exception = _exception()
            if error_code == exception.code:
                raise exception

        raise APIException(
            error_code,
            f"An unknown API error has occured: {response.get('message') or '...'}",
        )

    def _handle(self, response: httpx.Response, return_type: Type[R]) -> R:
        if not response.is_success:
            self._raise_error_code(response.json())
        return response.json()

    async def get_discord_account(self, id: int):
        """Get a Nexus account from a Discord user."""
        return Account(
            data=self._handle(
                await self._requests.get("/accounts/discord/" + str(id)),
                v1_AccountResponse,
            ),
        )

    async def get_roblox_account(self, id: int):
        """Get a Nexus account from a Roblox user."""
        return Account(
            data=self._handle(
                await self._requests.get("/accounts/roblox/" + str(id)),
                v1_AccountResponse,
            )
        )

    async def create_session(self, id: int):
        """Create a Nexus verification session for a Discord user."""
        return Session(
            self,
            data=self._handle(
                await self._requests.post(
                    "/sessions", json={"platform": Platform.DISCORD, "user_id": str(id)}
                ),
                v1_NewSessionResponse,
            ),
        )

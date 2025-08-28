from typing import Dict, Optional, TypeVar, Generic
from .exceptions import NexusException
from time import time
import asyncio
import httpx

R = TypeVar("R", bound=str)


class Bucket:
    def __init__(self, name: str, limit: int, remaining: int, reset_at: float):
        self.name = name
        self.limit = limit
        self.remaining = remaining
        self.reset_at = reset_at


class RateLimiter:
    def __init__(self):
        self.route_buckets: Dict[str, str] = {}
        self.buckets: Dict[str, Bucket] = {}

    def save_bucket(self, route: str, headers: httpx.Headers) -> None:
        bucket_name = headers.get("X-RateLimit-Bucket", "Unknown")
        limit = int(headers.get("X-RateLimit-Limit", 0))
        remaining = int(headers.get("X-RateLimit-Remaining", 0))
        reset_at = float(headers.get("X-RateLimit-Reset", time()))

        if bucket_name:
            self.route_buckets[route] = bucket_name
            self.buckets[bucket_name] = Bucket(bucket_name, limit, remaining, reset_at)

    def get_bucket(self, route: str) -> Optional[Bucket]:
        bucket_name = self.route_buckets.get(route)
        if bucket_name:
            return self.buckets.get(bucket_name)
        return None

    async def avoid_limit(self, route: str, max_retry_after: float) -> None:
        bucket = self.get_bucket(route)
        if bucket and bucket.remaining <= 0:
            wait_time = bucket.reset_at - time()
            if wait_time > 0:
                if wait_time > max_retry_after:
                    raise NexusException("Rate limit exceeded. Possibly IP banned.")
                await asyncio.sleep(wait_time)
            else:
                del self.buckets[bucket.name]

    async def wait_to_retry(
        self, headers: httpx.Headers, max_retry_after: float
    ) -> bool:
        retry_after = float(headers.get("X-RateLimit-Reset-After", 0))
        if retry_after > 0:
            if retry_after > max_retry_after:
                return False
            await asyncio.sleep(retry_after)
        return True


class Requests(Generic[R]):
    """Handles API requests with rate limit handling and retries."""

    def __init__(
        self,
        base_url: str,
        headers: Optional[Dict[str, str]] = None,
        session: Optional[httpx.AsyncClient] = None,
        max_retries: int = 3,
        max_retry_after: float = 15.0,
        timeout: float = 5.0,
    ):
        self._base_url = base_url.rstrip("/")
        self._headers = headers or {}
        self._session = session or httpx.AsyncClient()
        self._max_retries = max_retries
        self._max_retry_after = max_retry_after
        self._timeout = timeout

        self._rate_limiter = RateLimiter()

    def _can_retry(self, status_code: int, retry: int) -> bool:
        return (status_code == 429 or status_code >= 500) and retry < self._max_retries

    async def _make_request(
        self, method: str, route: R, retry: int = 0, **kwargs
    ) -> httpx.Response:
        await self._rate_limiter.avoid_limit(route, self._max_retry_after)

        url = f"{self._base_url}{route}"
        headers = {**self._headers, **kwargs.pop("headers", {})}

        try:
            response = await self._session.request(
                method,
                url,
                headers=headers,
                timeout=httpx.Timeout(self._timeout),
                **kwargs,
            )
        except httpx.ReadTimeout:
            if self._can_retry(500, retry):
                await asyncio.sleep(retry * 1.5)
                return await self._make_request(method, route, retry + 1, **kwargs)
            raise NexusException(
                f"Nexus API took too long to respond. ({retry}/{self._max_retries} retries) ({self._timeout}s timeout)"
            )

        self._rate_limiter.save_bucket(route, response.headers)

        if self._can_retry(response.status_code, retry):
            if await self._rate_limiter.wait_to_retry(
                response.headers, self._max_retry_after
            ):
                return await self._make_request(method, route, retry + 1, **kwargs)

        return response

    async def get(self, route: R, **kwargs):
        return await self._make_request("GET", route, **kwargs)

    async def post(self, route: R, **kwargs):
        return await self._make_request("POST", route, **kwargs)

    async def _close(self):
        await self._session.aclose()

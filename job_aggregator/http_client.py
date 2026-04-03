"""Small stdlib-only HTTP wrapper used by provider connectors."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any
from urllib import error, parse, request


DEFAULT_HEADERS = {
    "User-Agent": "job-aggregator/1.0 (+https://github.com/gnrtech/Iceberg)",
    "Accept": "application/json, text/plain, */*",
}


@dataclass(slots=True)
class HttpClient:
    """Tiny HTTP client with retries and JSON helpers."""

    timeout_seconds: int = 20
    retries: int = 2
    retry_sleep_seconds: float = 0.75

    def get_text(self, url: str, headers: dict[str, str] | None = None) -> str:
        return self._request(url=url, method="GET", headers=headers)

    def get_json(self, url: str, headers: dict[str, str] | None = None) -> Any:
        return json.loads(self.get_text(url=url, headers=headers))

    def post_json(
        self,
        url: str,
        payload: dict[str, Any],
        headers: dict[str, str] | None = None,
    ) -> Any:
        raw = json.dumps(payload).encode("utf-8")
        effective_headers = {"Content-Type": "application/json", **(headers or {})}
        body = self._request(url=url, method="POST", headers=effective_headers, data=raw)
        return json.loads(body)

    @staticmethod
    def absolute_url(base_url: str, href: str) -> str:
        """Build an absolute URL from base + relative/absolute href."""
        return parse.urljoin(base_url, href)

    def _request(
        self,
        url: str,
        method: str,
        headers: dict[str, str] | None = None,
        data: bytes | None = None,
    ) -> str:
        effective_headers = {**DEFAULT_HEADERS, **(headers or {})}
        last_error: Exception | None = None

        for attempt in range(self.retries + 1):
            req = request.Request(url=url, method=method, headers=effective_headers, data=data)
            try:
                with request.urlopen(req, timeout=self.timeout_seconds) as response:
                    return response.read().decode("utf-8", errors="replace")
            except (error.HTTPError, error.URLError, TimeoutError, ValueError) as exc:
                last_error = exc
                if attempt >= self.retries:
                    break
                time.sleep(self.retry_sleep_seconds * (attempt + 1))

        raise RuntimeError(f"HTTP request failed for {url!r}: {last_error}") from last_error


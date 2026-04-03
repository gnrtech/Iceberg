"""Portal detection based on URL and lightweight HTML cues."""

from __future__ import annotations

from urllib.parse import urlparse

from .http_client import HttpClient
from .models import PortalType


class PortalDetector:
    """Detect the provider type for a given careers portal URL."""

    def __init__(self, http_client: HttpClient | None = None) -> None:
        self.http_client = http_client

    def detect(self, url: str) -> PortalType:
        parsed = urlparse(url)
        host = (parsed.netloc or "").lower()
        path = (parsed.path or "").lower()
        full = f"{host}{path}"

        if "myworkdayjobs.com" in host or "workday" in full:
            return PortalType.WORKDAY
        if "greenhouse.io" in host or "/greenhouse" in path:
            return PortalType.GREENHOUSE
        if "lever.co" in host:
            return PortalType.LEVER

        # Optional HTML probe only when a client is supplied.
        if self.http_client is None:
            return PortalType.CUSTOM_HTML
        try:
            html = self.http_client.get_text(url).lower()
        except RuntimeError:
            return PortalType.CUSTOM_HTML

        if "myworkdayjobs.com" in html or "wd5.myworkdayjobs.com" in html:
            return PortalType.WORKDAY
        if "boards.greenhouse.io" in html:
            return PortalType.GREENHOUSE
        if "jobs.lever.co" in html:
            return PortalType.LEVER
        return PortalType.CUSTOM_HTML


def detect_portal_type(url: str, http_client: HttpClient | None = None) -> PortalType:
    """Functional helper for quick portal type detection."""
    return PortalDetector(http_client=http_client).detect(url)


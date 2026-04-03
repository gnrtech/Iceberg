"""Fallback parser for custom HTML careers pages."""

from __future__ import annotations

from html.parser import HTMLParser
from urllib.parse import urljoin

from ..http_client import HttpClient
from ..models import CompanyInput, JobPosting, PortalType
from .base import BaseProvider


class _AnchorParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self._in_anchor = False
        self._current_href = ""
        self._current_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        href = ""
        for key, value in attrs:
            if key.lower() == "href" and value:
                href = value
                break
        if not href:
            return
        self._in_anchor = True
        self._current_href = href
        self._current_text = []

    def handle_data(self, data: str) -> None:
        if self._in_anchor:
            self._current_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() != "a" or not self._in_anchor:
            return
        text = "".join(self._current_text).strip()
        self.links.append((self._current_href, text))
        self._in_anchor = False
        self._current_href = ""
        self._current_text = []


class CustomHtmlProvider(BaseProvider):
    """Best-effort extraction when no public API exists."""

    portal_type = PortalType.CUSTOM_HTML

    def __init__(self, http_client: HttpClient) -> None:
        self.http_client = http_client

    def fetch_jobs(self, company: CompanyInput) -> list[JobPosting]:
        html = self.http_client.get_text(company.url)
        parser = _AnchorParser()
        parser.feed(html)

        jobs: list[JobPosting] = []
        seen_urls: set[str] = set()

        for href, text in parser.links:
            href_l = href.lower()
            text_l = text.lower()
            if "job" not in href_l and "career" not in href_l and "job" not in text_l:
                continue

            full_url = urljoin(company.url, href)
            if full_url in seen_urls:
                continue
            seen_urls.add(full_url)
            title = text if text else "Career Opportunity"
            jobs.append(
                JobPosting(
                    job_title=title,
                    company_name=company.name,
                    location="Unknown",
                    job_url=full_url,
                    portal_type=self.portal_type,
                )
            )
        return jobs

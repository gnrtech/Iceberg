"""Lever API extractor."""

from __future__ import annotations

from urllib.parse import urlparse

from ..models import CompanyInput, JobPosting, PortalType
from .base import BaseProvider


class LeverProvider(BaseProvider):
    portal_type = PortalType.LEVER

    def __init__(self, http_client) -> None:
        self.http_client = http_client

    def fetch_jobs(self, company: CompanyInput) -> list[JobPosting]:
        handle = self._extract_handle(company.url)
        api_url = f"https://api.lever.co/v0/postings/{handle}?mode=json"
        data = self.http_client.get_json(api_url)
        jobs: list[JobPosting] = []
        if not isinstance(data, list):
            return jobs

        for item in data:
            title = str(item.get("text") or "").strip()
            location = str((item.get("categories") or {}).get("location") or "").strip()
            apply_url = str(item.get("hostedUrl") or "").strip()
            if not title or not apply_url:
                continue
            jobs.append(
                JobPosting(
                    job_title=title,
                    company_name=company.name,
                    location=location or "Unknown",
                    job_url=apply_url,
                    portal_type=self.portal_type,
                )
            )
        return jobs

    @staticmethod
    def _extract_handle(url: str) -> str:
        parsed = urlparse(url)
        host = parsed.netloc.lower()
        if "jobs.lever.co" in host:
            parts = [part for part in parsed.path.split("/") if part]
            if parts:
                return parts[0]
        # fallback: last path component
        parts = [part for part in parsed.path.split("/") if part]
        if parts:
            return parts[-1]
        return host.split(".")[0]

"""Greenhouse API-based job extractor."""

from __future__ import annotations

from ..http_client import HttpClient
from ..models import CompanyInput, JobPosting, PortalType
from .base import BaseProvider


class GreenhouseProvider(BaseProvider):
    """Extract jobs from Greenhouse board API."""

    portal_type = PortalType.GREENHOUSE

    def __init__(self, http_client: HttpClient) -> None:
        self.http_client = http_client

    @staticmethod
    def _extract_board_token(url: str) -> str:
        cleaned = url.rstrip("/")
        # Common patterns:
        # - https://boards.greenhouse.io/company
        # - https://job-boards.greenhouse.io/company
        token = cleaned.split("/")[-1]
        return token

    def fetch_jobs(self, company: CompanyInput) -> list[JobPosting]:
        board_token = self._extract_board_token(company.url)
        api_url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs"
        data = self.http_client.get_json(api_url)

        jobs: list[JobPosting] = []
        for item in data.get("jobs", []):
            location = item.get("location", {}).get("name", "")
            absolute_url = item.get("absolute_url", "")
            title = item.get("title", "")
            if not (title and absolute_url):
                continue
            jobs.append(
                JobPosting(
                    job_title=title,
                    company_name=company.name,
                    location=location or "Unknown",
                    job_url=absolute_url,
                    portal_type=self.portal_type,
                )
            )
        return jobs

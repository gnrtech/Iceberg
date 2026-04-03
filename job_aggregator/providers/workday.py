"""Workday provider extraction using API-first strategy."""

from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

from ..http_client import HttpClient
from ..models import CompanyInput, JobPosting, PortalType
from .base import BaseProvider


class WorkdayProvider(BaseProvider):
    """Extract jobs from Workday careers portals."""

    portal_type = PortalType.WORKDAY

    def __init__(self, http_client: HttpClient, page_size: int = 20) -> None:
        self.http_client = http_client
        self.page_size = page_size

    def fetch_jobs(self, company: CompanyInput) -> list[JobPosting]:
        endpoints = self._candidate_endpoints(company.url)
        last_error: Exception | None = None
        for endpoint in endpoints:
            try:
                jobs = self._fetch_from_endpoint(company, endpoint)
                if jobs:
                    return jobs
            except Exception as exc:  # noqa: BLE001
                last_error = exc
        if last_error:
            raise RuntimeError(
                f"Unable to extract Workday jobs for {company.name}."
            ) from last_error
        return []

    def _fetch_from_endpoint(self, company: CompanyInput, endpoint: str) -> list[JobPosting]:
        all_jobs: list[JobPosting] = []
        offset = 0

        while True:
            payload = {"limit": self.page_size, "offset": offset, "searchText": ""}
            response = self.http_client.post_json(endpoint, payload=payload)
            postings = response.get("jobPostings", []) or response.get("jobPostingsList", [])
            if not postings:
                break

            mapped = [self._map_posting(company, job, base_url=company.url) for job in postings]
            all_jobs.extend([job for job in mapped if job is not None])
            if len(postings) < self.page_size:
                break
            offset += self.page_size
        return all_jobs

    def _candidate_endpoints(self, careers_url: str) -> list[str]:
        parsed = urlparse(careers_url)
        base_path = parsed.path.rstrip("/")
        candidates = [
            f"{parsed.scheme}://{parsed.netloc}{base_path}/jobs",
        ]
        path_parts = [part for part in base_path.split("/") if part]
        if len(path_parts) >= 1:
            tenant = path_parts[0]
            site = path_parts[1] if len(path_parts) > 1 else path_parts[0]
            candidates.append(
                f"{parsed.scheme}://{parsed.netloc}/wday/cxs/{tenant}/{site}/jobs"
            )
            candidates.append(
                f"{parsed.scheme}://{parsed.netloc}/wday/cxs/{tenant}/{site}/jobs?page=0"
            )
        # Preserve order while deduplicating.
        seen: set[str] = set()
        unique: list[str] = []
        for endpoint in candidates:
            if endpoint in seen:
                continue
            seen.add(endpoint)
            unique.append(endpoint)
        return unique

    def _map_posting(
        self, company: CompanyInput, item: dict[str, Any], base_url: str
    ) -> JobPosting | None:
        title = item.get("title") or item.get("jobTitle")
        location = item.get("locationsText") or item.get("location")
        external_path = item.get("externalPath") or item.get("externalPath")
        if not title:
            return None
        if external_path:
            job_url = (
                f"{base_url.rstrip('/')}{external_path}"
                if str(external_path).startswith("/")
                else str(external_path)
            )
        else:
            req_id = item.get("bulletFields", [{}])
            if isinstance(req_id, list) and req_id:
                req = req_id[0]
            else:
                req = {}
            job_url = base_url
            if isinstance(req, dict) and req.get("value"):
                job_url = f"{base_url.rstrip('/')}/job/{req['value']}"
        return JobPosting(
            job_title=str(title).strip(),
            company_name=company.name,
            location=str(location or "Unknown").strip(),
            job_url=str(job_url).strip(),
            portal_type=self.portal_type,
            metadata={"raw_id": str(item.get("id", ""))},
        )

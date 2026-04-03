"""Aggregation pipeline that orchestrates providers and filtering."""

from __future__ import annotations

from collections.abc import Iterable

from .detector import PortalDetector
from .filters import apply_filters, dedupe_by_url
from .formatter import format_jobs_text
from .http_client import HttpClient
from .models import CompanyInput, CompanyScanReport, JobPosting, PortalType
from .providers import BaseProvider, CustomHtmlProvider, GreenhouseProvider, LeverProvider, WorkdayProvider


class JobAggregator:
    """Coordinates extraction, filtering, and final formatting."""

    def __init__(self, timeout: int = 20, retries: int = 2) -> None:
        self.http = HttpClient(timeout_seconds=timeout, retries=retries)
        self.detector = PortalDetector(http_client=self.http)
        self._providers: dict[PortalType, BaseProvider] = {
            PortalType.WORKDAY: WorkdayProvider(self.http),
            PortalType.GREENHOUSE: GreenhouseProvider(self.http),
            PortalType.LEVER: LeverProvider(self.http),
            PortalType.CUSTOM_HTML: CustomHtmlProvider(self.http),
        }
        self.last_reports: list[CompanyScanReport] = []

    def collect_jobs(self, companies: Iterable[CompanyInput]) -> list[JobPosting]:
        """Collect jobs from all company sources with graceful error handling."""
        self.last_reports = []
        all_jobs: list[JobPosting] = []

        for company in companies:
            portal_type = self.detector.detect(company.url)
            provider = self._providers[portal_type]
            report = CompanyScanReport(company_name=company.name, url=company.url, portal_type=portal_type)
            try:
                jobs = provider.fetch_jobs(company)
                all_jobs.extend(jobs)
                report.extracted_count = len(jobs)
            except Exception as exc:  # noqa: BLE001
                report.error = str(exc)
            self.last_reports.append(report)
        return all_jobs

    def run(
        self,
        companies: Iterable[CompanyInput],
        keywords: list[str],
        locations: list[str],
        limit: int = 15,
    ) -> list[JobPosting]:
        """Run extraction and filtering, returning normalized postings."""
        jobs = self.collect_jobs(companies)
        jobs = apply_filters(jobs, keywords=keywords, locations=locations)
        jobs = dedupe_by_url(jobs)
        return jobs[:limit]

    def aggregate(
        self,
        companies: Iterable[CompanyInput],
        keywords: list[str],
        location_filters: list[str],
        top_n: int = 15,
    ) -> tuple[list[JobPosting], str]:
        """Run full pipeline and return jobs + formatted output."""
        jobs = self.run(
            companies=companies,
            keywords=keywords,
            locations=location_filters,
            limit=top_n,
        )
        return jobs, format_jobs_text(jobs)


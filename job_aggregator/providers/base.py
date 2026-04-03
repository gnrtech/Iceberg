"""Provider base interfaces."""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..models import CompanyInput, JobPosting


class BaseProvider(ABC):
    """Common interface for all portal providers."""

    @abstractmethod
    def fetch_jobs(self, company: CompanyInput) -> list[JobPosting]:
        """Fetch and normalize job postings."""

"""Core models for the job aggregation pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class PortalType(str, Enum):
    """Supported job portal types."""

    WORKDAY = "workday"
    GREENHOUSE = "greenhouse"
    LEVER = "lever"
    CUSTOM_HTML = "custom_html"


@dataclass(slots=True, frozen=True)
class CompanyInput:
    """Input company descriptor."""

    name: str
    url: str


@dataclass(slots=True)
class JobPosting:
    """Normalized job posting extracted from a career portal."""

    job_title: str
    company_name: str
    location: str
    job_url: str
    portal_type: PortalType
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class CompanyScanReport:
    """Per-company extraction report for observability."""

    company_name: str
    url: str
    portal_type: PortalType
    extracted_count: int = 0
    error: str | None = None


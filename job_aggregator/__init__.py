"""Job aggregation package for IT careers portals."""

from .aggregator import JobAggregator
from .models import CompanyInput, JobPosting, PortalType

__all__ = [
    "JobAggregator",
    "CompanyInput",
    "JobPosting",
    "PortalType",
]

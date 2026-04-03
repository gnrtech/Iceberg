"""Tests for portal type detector."""

from job_aggregator.detector import detect_portal_type
from job_aggregator.http_client import HttpClient
from job_aggregator.models import PortalType


def test_detect_workday() -> None:
    assert (
        detect_portal_type(
            "https://accenture.wd3.myworkdayjobs.com/accenturecareers",
            http_client=HttpClient(),
        )
        == PortalType.WORKDAY
    )


def test_detect_custom() -> None:
    assert (
        detect_portal_type(
            "https://careers.infosys.com",
            http_client=HttpClient(retries=0, timeout_seconds=1),
        )
        == PortalType.CUSTOM_HTML
    )


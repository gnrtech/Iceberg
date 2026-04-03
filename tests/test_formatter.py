from datetime import date

from job_aggregator.formatter import format_jobs_text
from job_aggregator.models import JobPosting, PortalType


def test_format_jobs_text_renders_expected_header_and_blocks() -> None:
    jobs = [
        JobPosting(
            job_title="Data Engineer",
            company_name="Accenture",
            location="Bangalore, India",
            job_url="https://example.com/job/1",
            portal_type=PortalType.WORKDAY,
        )
    ]
    result = format_jobs_text(jobs, report_date=date(2026, 4, 3))
    assert "🔥 Data Engineer Jobs (India) – 2026-04-03" in result
    assert "👉 Data Engineer – Accenture" in result
    assert "📍 Bangalore, India" in result
    assert "🔗 https://example.com/job/1" in result

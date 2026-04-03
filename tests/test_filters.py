from job_aggregator.filters import dedupe_by_url, apply_filters
from job_aggregator.models import JobPosting, PortalType


def test_filtering_by_keyword_and_location() -> None:
    jobs = [
        JobPosting(
            job_title="Data Engineer",
            company_name="A",
            location="Bangalore, India",
            job_url="https://example.com/1",
            portal_type=PortalType.WORKDAY,
        ),
        JobPosting(
            job_title="Frontend Developer",
            company_name="A",
            location="Mumbai, India",
            job_url="https://example.com/2",
            portal_type=PortalType.WORKDAY,
        ),
    ]
    filtered = apply_filters(
        jobs,
        keywords=["data engineer", "python"],
        locations=["bangalore", "hyderabad", "india"],
    )
    assert len(filtered) == 1
    assert filtered[0].job_title == "Data Engineer"


def test_dedupe_by_url() -> None:
    jobs = [
        JobPosting(
            job_title="Data Engineer",
            company_name="A",
            location="Bangalore",
            job_url="https://example.com/1",
            portal_type=PortalType.WORKDAY,
        ),
        JobPosting(
            job_title="Data Engineer II",
            company_name="B",
            location="Hyderabad",
            job_url="https://example.com/1",
            portal_type=PortalType.GREENHOUSE,
        ),
    ]
    deduped = dedupe_by_url(jobs)
    assert len(deduped) == 1
    assert deduped[0].company_name == "A"

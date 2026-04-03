"""Text formatter for final job output."""

from __future__ import annotations

from datetime import date

from .models import JobPosting


def format_jobs_text(jobs: list[JobPosting], report_date: date | None = None) -> str:
    """Render job results in requested WhatsApp/X-friendly format."""
    output_date = report_date or date.today()
    lines = [f"\U0001f525 Data Engineer Jobs (India) \u2013 {output_date.isoformat()}", ""]
    for job in jobs:
        lines.append(f"\U0001f449 {job.job_title} \u2013 {job.company_name}")
        lines.append(f"\U0001f4cd {job.location}")
        lines.append(f"\U0001f517 {job.job_url}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"

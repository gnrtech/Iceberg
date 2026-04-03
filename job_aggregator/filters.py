"""Filtering, deduplication, and limiting helpers."""

from __future__ import annotations

from collections.abc import Iterable

from .models import JobPosting


def _normalize(value: str) -> str:
    return value.strip().lower()


def matches_keywords(job: JobPosting, keywords: Iterable[str]) -> bool:
    """Return True if any keyword appears in title or metadata."""
    if not keywords:
        return True
    haystack_parts = [job.job_title, job.location]
    haystack_parts.extend(str(v) for v in job.metadata.values())
    haystack = " ".join(_normalize(part) for part in haystack_parts if part)
    return any(_normalize(keyword) in haystack for keyword in keywords)


def matches_location(job: JobPosting, locations: Iterable[str]) -> bool:
    """Return True if any location term appears in the location text."""
    if not locations:
        return True
    location = _normalize(job.location)
    return any(_normalize(term) in location for term in locations)


def filter_jobs(
    jobs: Iterable[JobPosting],
    keywords: Iterable[str],
    locations: Iterable[str],
) -> list[JobPosting]:
    """Apply keyword and location filters to jobs."""
    return [
        job
        for job in jobs
        if matches_keywords(job, keywords) and matches_location(job, locations)
    ]


def deduplicate_jobs(jobs: Iterable[JobPosting]) -> list[JobPosting]:
    """Deduplicate postings by canonical job URL, preserving order."""
    seen: set[str] = set()
    deduped: list[JobPosting] = []
    for job in jobs:
        key = job.job_url.strip()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(job)
    return deduped


def limit_jobs(jobs: Iterable[JobPosting], max_items: int) -> list[JobPosting]:
    """Limit final output size while preserving original rank order."""
    if max_items <= 0:
        return []
    output: list[JobPosting] = []
    for job in jobs:
        output.append(job)
        if len(output) >= max_items:
            break
    return output


def apply_filters(
    jobs: Iterable[JobPosting],
    keywords: Iterable[str],
    locations: Iterable[str],
) -> list[JobPosting]:
    """Backward-compatible alias for filter_jobs."""
    return filter_jobs(jobs, keywords=keywords, locations=locations)


def dedupe_by_url(jobs: Iterable[JobPosting]) -> list[JobPosting]:
    """Backward-compatible alias for deduplicate_jobs."""
    return deduplicate_jobs(jobs)

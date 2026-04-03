"""CLI entrypoint for the job aggregation system."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .aggregator import JobAggregator
from .formatter import format_jobs_text
from .models import CompanyInput


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="job-aggregator",
        description="Aggregate and filter jobs from company career portals.",
    )
    parser.add_argument(
        "--input-json",
        required=True,
        help="Path to input JSON containing companies, keywords, and locations.",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=None,
        help="Maximum number of jobs in final output.",
    )
    parser.add_argument(
        "--json-output",
        action="store_true",
        help="Print normalized jobs as JSON instead of formatted text.",
    )
    return parser


def _load_input(path: Path) -> tuple[list[CompanyInput], list[str], list[str], int]:
    payload: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    companies = [
        CompanyInput(name=item["name"], url=item["url"]) for item in payload["companies"]
    ]
    keywords = [str(k) for k in payload["keywords"]]
    locations = [str(loc) for loc in payload["locations"]]
    limit = int(payload.get("limit", 15))
    return companies, keywords, locations, limit


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    companies, keywords, locations, default_limit = _load_input(Path(args.input_json))
    top_n = args.top if args.top is not None else default_limit

    aggregator = JobAggregator()
    jobs = aggregator.run(
        companies=companies,
        keywords=keywords,
        locations=locations,
        limit=top_n,
    )

    if args.json_output:
        print(json.dumps([asdict(job) for job in jobs], indent=2, ensure_ascii=False))
        return

    print(format_jobs_text(jobs))


if __name__ == "__main__":
    main()

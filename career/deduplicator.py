from __future__ import annotations

from .models import JobListing
from .normalizer import canonical_url, job_fingerprint


def deduplicate(jobs: list[JobListing]) -> list[JobListing]:
    source_ids: set[tuple[str, str]] = set()
    urls: set[str] = set()
    fingerprints: set[str] = set()
    unique: list[JobListing] = []

    for job in jobs:
        source_id = (job.source.casefold(), job.external_id) if job.external_id else None
        url = canonical_url(job.url)
        fingerprint = job_fingerprint(job)
        if (source_id and source_id in source_ids) or url in urls or fingerprint in fingerprints:
            continue
        if source_id:
            source_ids.add(source_id)
        urls.add(url)
        fingerprints.add(fingerprint)
        unique.append(job)
    return unique

from career.models import JobListing
from career.scorer import score_job

from .conftest import javascript_profile


def test_score_is_deterministic_and_bounded():
    job = JobListing(
        source="Lever", title="Backend Developer", company="Acme", url="https://example.com/1",
        seniority="junior", workplace_type="remote",
        technologies=["TypeScript", "Node.js", "Prisma", "PostgreSQL", "Docker"],
    )

    assert score_job(job, javascript_profile()).score == 100
    assert score_job(job, javascript_profile()).score == 100

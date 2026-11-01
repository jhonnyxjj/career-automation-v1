from __future__ import annotations

from .config import SCORE_WEIGHTS
from .models import JobListing, ScoreComponent, SearchProfile


def score_job(job: JobListing, profile: SearchProfile) -> JobListing:
    technologies = set(job.technologies)
    complementary = profile.desired_technologies - profile.primary_languages - profile.frameworks - profile.databases - profile.cloud_devops
    checks = [
        ("Linguagem principal", bool(technologies & profile.primary_languages), SCORE_WEIGHTS.primary_language, bool(technologies)),
        ("Senioridade", job.seniority in profile.allowed_seniorities, SCORE_WEIGHTS.seniority, bool(job.seniority)),
        ("Framework", bool(technologies & profile.frameworks), SCORE_WEIGHTS.framework, bool(technologies)),
        ("Tecnologias complementares", bool(technologies & complementary), SCORE_WEIGHTS.complementary_stack, bool(technologies)),
        ("Banco de dados", bool(technologies & profile.databases), SCORE_WEIGHTS.database, bool(technologies)),
        ("Cloud e DevOps", bool(technologies & profile.cloud_devops), SCORE_WEIGHTS.cloud_devops, bool(technologies)),
        ("Modalidade", job.workplace_type in profile.allowed_workplaces, SCORE_WEIGHTS.workplace, bool(job.workplace_type)),
    ]
    breakdown = [ScoreComponent(label=label, points=weight if matched else 0, status="match" if matched else "not_identified" if known else "unknown") for label, matched, weight, known in checks]
    return job.model_copy(update={"score": min(sum(item.points for item in breakdown), 100), "score_version": "1", "score_breakdown": breakdown})

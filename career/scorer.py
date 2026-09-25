from __future__ import annotations

from .config import SCORE_WEIGHTS
from .models import JobListing, SearchProfile


def score_job(job: JobListing, profile: SearchProfile) -> JobListing:
    technologies = set(job.technologies)
    score = 0
    if technologies.intersection(profile.primary_languages):
        score += SCORE_WEIGHTS.primary_language
    if job.seniority in profile.allowed_seniorities:
        score += SCORE_WEIGHTS.seniority
    if technologies.intersection(profile.frameworks):
        score += SCORE_WEIGHTS.framework
    complementary = profile.desired_technologies - profile.primary_languages - profile.frameworks - profile.databases - profile.cloud_devops
    if technologies.intersection(complementary):
        score += SCORE_WEIGHTS.complementary_stack
    if technologies.intersection(profile.databases):
        score += SCORE_WEIGHTS.database
    if technologies.intersection(profile.cloud_devops):
        score += SCORE_WEIGHTS.cloud_devops
    if job.workplace_type in profile.allowed_workplaces:
        score += SCORE_WEIGHTS.workplace
    return job.model_copy(update={"score": min(score, 100)})

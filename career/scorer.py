from __future__ import annotations

import re

from .config import SCORE_WEIGHTS
from .models import JobListing, ScoreComponent, SearchProfile
from .normalizer import normalized_text


_YEARS = r"\d{1,3}(?:\s*(?:a|ate|to|[-–—])\s*\d{1,3})?\s*(?:anos?|years?)"
_EXPERIENCE_YEARS = re.compile(
    rf"\b(?:{_YEARS}\s+(?:de|of)\s+(?:experiencia|experience)|"
    rf"(?:experiencia|experience)\s+(?:de|of)\s+{_YEARS})\b"
)


def _mentions_two_to_three_years(description: str | None) -> bool:
    for sentence in re.split(r"[.;\n]", description or ""):
        value = normalized_text(sentence)
        if re.search(r"\b(?:nao|sem|not|dispensad[ao])\b", value) or ("experience" in value and re.search(r"\bno\b", value)):
            continue
        for match in _EXPERIENCE_YEARS.finditer(value):
            years = [int(number) for number in re.findall(r"\d+", match.group())]
            if years and all(2 <= year <= 3 for year in years):
                return True
    return False


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
    score = min(sum(item.points for item in breakdown), 100)
    if _mentions_two_to_three_years(job.description):
        penalty = min(score, SCORE_WEIGHTS.experience_penalty)
        breakdown.append(ScoreComponent(label="Menção de 2–3 anos de experiência", points=-penalty, status="penalty"))
        score -= penalty
    return job.model_copy(update={"score": score, "score_version": "2", "score_breakdown": breakdown})

from __future__ import annotations

import re

from .models import CandidateProfile, JobListing, ResumeTemplateData
from .normalizer import normalized_text


class ResumeTailoringService:
    """Prioritizes truthful candidate content for a normalized vacancy."""

    def tailor(self, candidate: CandidateProfile, job: JobListing) -> ResumeTemplateData:
        job_terms = {normalized_text(technology) for technology in job.technologies}
        job_text = normalized_text(f"{job.title} {job.description or ''}")
        def matches_skill(item: str) -> bool:
            skill = normalized_text(item)
            return bool(skill) and (skill in job_terms or bool(re.search(rf"(?<!\w){re.escape(skill)}(?!\w)", job_text)))

        skills = sorted(
            [group.model_copy(update={"items": sorted(group.items, key=matches_skill, reverse=True)}) for group in candidate.technical_skills],
            key=lambda group: sum(matches_skill(item) for item in group.items),
            reverse=True,
        )
        return ResumeTemplateData(
            personal=candidate.personal,
            professional_summary=candidate.professional_summary,
            technical_skills=skills,
            experiences=self._prioritize(candidate.experiences, job_text, job_terms),
            projects=self._prioritize(candidate.projects, job_text, job_terms),
            education=candidate.education,
        )

    @staticmethod
    def _prioritize(items: list[object], job_text: str, job_terms: set[str]) -> list[object]:
        def relevance(item: object) -> int:
            text = normalized_text(" ".join(str(value) for value in item.__dict__.values() if value))
            return sum(bool(term) and bool(re.search(rf"(?<!\w){re.escape(term)}(?!\w)", text)) for term in job_terms) + sum(word in text for word in job_text.split() if len(word) > 4)

        return sorted(items, key=relevance, reverse=True)

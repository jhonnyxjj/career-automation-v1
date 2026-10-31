from career.models import CandidateProfile, JobListing, ResumeExperience, ResumePersonalDetails, TechnicalSkillGroup
from career.tailoring import ResumeTailoringService


def test_tailoring_only_reorders_truthful_candidate_content() -> None:
    candidate = CandidateProfile(
        id="original-1",
        personal=ResumePersonalDetails(name="Pessoa"),
        technical_skills=[
            TechnicalSkillGroup(category="Cloud", items=["AWS"]),
            TechnicalSkillGroup(category="Backend", items=["Python"]),
        ],
        experiences=[
            ResumeExperience(company="A", position="Dev", period="2024", bullets=["Usei Python"]),
            ResumeExperience(company="B", position="Dev", period="2025", bullets=["Usei AWS"]),
        ],
    )
    job = JobListing(source="source", title="AWS engineer", company="Acme", url="https://example.com", technologies=["AWS"])

    tailored = ResumeTailoringService().tailor(candidate, job)

    assert tailored.technical_skills[0].category == "Cloud"
    assert tailored.experiences[0].company == "B"
    assert "Kubernetes" not in [item for group in tailored.technical_skills for item in group.items]


def test_prioritizes_matching_skills_without_changing_original() -> None:
    candidate = CandidateProfile(id="1", personal=ResumePersonalDetails(name="Pessoa"), technical_skills=[
        TechnicalSkillGroup(category="Linguagens", items=["Java", "Python", "TypeScript"]),
    ])
    job = JobListing(source="source", title="Python developer", company="Acme", url="https://example.com", technologies=["Python"])
    tailored = ResumeTailoringService().tailor(candidate, job)
    assert tailored.technical_skills[0].items == ["Python", "Java", "TypeScript"]
    assert candidate.technical_skills[0].items == ["Java", "Python", "TypeScript"]


def test_java_does_not_match_javascript() -> None:
    candidate = CandidateProfile(id="1", personal=ResumePersonalDetails(name="Pessoa"), technical_skills=[
        TechnicalSkillGroup(category="Linguagens", items=["Java", "Python"]),
    ])
    job = JobListing(source="source", title="JavaScript and Python", company="Acme", url="https://example.com", technologies=["Python"])
    assert ResumeTailoringService().tailor(candidate, job).technical_skills[0].items == ["Python", "Java"]

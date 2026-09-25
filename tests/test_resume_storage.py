from pathlib import Path

from career.models import CandidateProfile, JobListing, ResumePersonalDetails
from career.resume_storage import ResumeRepository


def test_repository_preserves_original_and_records_generated_resume(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("career.resume_storage.RESUMES_DIR", tmp_path)
    profile = CandidateProfile(id="original-1", personal=ResumePersonalDetails(name="Pessoa"))
    job = JobListing(source="source", title="Dev", company="Acme", url="https://example.com", external_id="job-1")
    repository = ResumeRepository()

    original_path = repository.save_original(profile)
    generated = repository.generate_tailored(profile, job)

    assert original_path.exists()
    assert Path(generated.latex_path).exists()
    metadata = Path(generated.latex_path).with_name("generated-resume.json")
    assert metadata.exists()
    assert '"original_resume_id": "original-1"' in metadata.read_text(encoding="utf-8")

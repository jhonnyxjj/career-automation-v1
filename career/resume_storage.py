from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import shutil
from uuid import uuid4

from .latex import LaTeXRenderer
from .models import CandidateProfile, GeneratedResume, JobListing
from .tailoring import ResumeTailoringService


RESUMES_DIR = Path(".data") / "resumes"


class ResumeRepository:
    """Filesystem persistence that never overwrites an original resume."""

    def save_original(self, profile: CandidateProfile) -> Path:
        path = RESUMES_DIR / "original" / f"{profile.id}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            raise FileExistsError(f"O currículo original {profile.id} já existe.")
        path.write_text(profile.model_dump_json(indent=2), encoding="utf-8")
        return path

    def load_original(self, profile_id: str) -> CandidateProfile:
        path = RESUMES_DIR / "original" / f"{profile_id}.json"
        if not path.exists():
            raise FileNotFoundError("Perfil não encontrado.")
        return CandidateProfile.model_validate_json(path.read_text(encoding="utf-8"))

    def generate_tailored(self, profile: CandidateProfile, job: JobListing) -> GeneratedResume:
        generated_id = str(uuid4())
        directory = RESUMES_DIR / "tailored" / generated_id
        data = ResumeTailoringService().tailor(profile, job)
        renderer = LaTeXRenderer()
        tex_path = renderer.write_tex(data, directory / "resume.tex")
        pdf_path = None
        if shutil.which("pdflatex"):
            try:
                pdf_path = renderer.render_pdf(tex_path)
            except (RuntimeError, OSError):
                # The generated TeX remains available even if PDF compilation fails.
                pass
        generated = GeneratedResume(
            id=generated_id,
            original_resume_id=profile.id,
            job_id=job.external_id or job.url,
            generated_at=datetime.now(timezone.utc),
            latex_path=str(tex_path),
            pdf_path=str(pdf_path) if pdf_path else None,
        )
        (directory / "generated-resume.json").write_text(generated.model_dump_json(indent=2), encoding="utf-8")
        return generated

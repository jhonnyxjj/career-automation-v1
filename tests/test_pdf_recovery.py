import subprocess
from pathlib import Path

import pytest

from career.latex import LaTeXRenderer
from career.models import CandidateProfile, JobListing, ResumePersonalDetails
from career.resume_storage import ResumeRepository


@pytest.mark.parametrize("failure", [RuntimeError("compile failed"), OSError("compiler unavailable")])
def test_compiler_failure_preserves_tex_and_metadata(monkeypatch, tmp_path: Path, failure):
    monkeypatch.setattr("career.resume_storage.RESUMES_DIR", tmp_path)
    monkeypatch.setattr("career.resume_storage.shutil.which", lambda _: "/usr/bin/pdflatex")
    def fail(*_args):
        raise failure
    monkeypatch.setattr(LaTeXRenderer, "render_pdf", fail)
    profile = CandidateProfile(id="test", personal=ResumePersonalDetails(name="Pessoa fictícia"))
    job = JobListing(source="Teste", title="Backend", company="Empresa", url="https://example.com")
    generated = ResumeRepository().generate_tailored(profile, job)
    assert generated.pdf_path is None
    assert Path(generated.latex_path).is_file()
    assert Path(generated.latex_path).with_name("generated-resume.json").is_file()


def test_pdflatex_timeout_is_bounded(monkeypatch, tmp_path: Path):
    monkeypatch.setattr("career.latex.shutil.which", lambda _: "/usr/bin/pdflatex")
    def timeout(*args, **kwargs):
        assert kwargs["timeout"] == 30
        raise subprocess.TimeoutExpired(args[0], kwargs["timeout"])
    monkeypatch.setattr("career.latex.subprocess.run", timeout)
    with pytest.raises(RuntimeError, match="Tempo limite"):
        LaTeXRenderer().render_pdf(tmp_path / "resume.tex")

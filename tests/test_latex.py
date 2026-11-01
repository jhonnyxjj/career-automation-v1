import subprocess

import pytest

from career.latex import LaTeXRenderer, escape_latex
from career.models import ResumePersonalDetails, ResumeTemplateData, TechnicalSkillGroup


def test_escape_latex_covers_special_characters() -> None:
    assert escape_latex(r"\\{}$&#%_~^") == (
        r"\textbackslash{}\textbackslash{}\{\}\$\&\#\%\_\textasciitilde{}\textasciicircum{}"
    )


def test_pdf_failure_does_not_expose_compiler_output(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr("career.latex.shutil.which", lambda _: "/usr/bin/pdflatex")
    monkeypatch.setattr("career.latex.subprocess.run", lambda *args, **kwargs: subprocess.CompletedProcess(args, 1, stdout="private data", stderr="private data"))
    with pytest.raises(RuntimeError) as error:
        LaTeXRenderer().render_pdf(tmp_path / "resume.tex")
    assert "private data" not in str(error.value)


def test_renderer_escapes_data_and_omits_empty_sections() -> None:
    data = ResumeTemplateData(
        personal=ResumePersonalDetails(name="Ana & Co", headline="Backend #1"),
        technical_skills=[TechnicalSkillGroup(category="Dados", items=["SQL_1"])],
    )

    document = LaTeXRenderer().render_tex(data)

    assert r"\textbf{Ana \& Co}" in document
    assert r"SQL\_1" in document
    assert r"\section{Resumo Profissional}" not in document
    assert r"\section{Experiência Profissional}" not in document
    assert LaTeXRenderer._section("Projetos", "conteúdo") == "\\section{Projetos}\nconteúdo"

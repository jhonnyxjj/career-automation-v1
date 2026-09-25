from career.latex import LaTeXRenderer, escape_latex
from career.models import ResumePersonalDetails, ResumeTemplateData, TechnicalSkillGroup


def test_escape_latex_covers_special_characters() -> None:
    assert escape_latex(r"\\{}$&#%_~^") == (
        r"\textbackslash{}\textbackslash{}\{\}\$\&\#\%\_\textasciitilde{}\textasciicircum{}"
    )


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

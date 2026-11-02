from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from .models import ResumeEducation, ResumeExperience, ResumeProject, ResumeTemplateData


TEMPLATE_PATH = Path(__file__).with_name("templates") / "resume.tex"


def escape_latex(value: str) -> str:
    """Escapes untrusted resume and vacancy text before it reaches LaTeX."""

    replacements = {
        "\\": r"\textbackslash{}",
        "{": r"\{",
        "}": r"\}",
        "$": r"\$",
        "&": r"\&",
        "#": r"\#",
        "%": r"\%",
        "_": r"\_",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(character, character) for character in value)


class LaTeXRenderer:
    """Renders already-selected resume data; it has no matching rules."""

    def render_tex(self, data: ResumeTemplateData) -> str:
        template = TEMPLATE_PATH.read_text(encoding="utf-8")
        return template.replace("% RESUME_CONTENT %", self._content(data))

    def write_tex(self, data: ResumeTemplateData, output_path: Path) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(self.render_tex(data), encoding="utf-8")
        return output_path

    def render_pdf(self, tex_path: Path) -> Path:
        compiler = shutil.which("pdflatex")
        if compiler is None:
            raise RuntimeError("pdflatex não está instalado; o arquivo .tex foi preservado para compilação posterior.")
        try:
            result = subprocess.run(
                [compiler, "-interaction=nonstopmode", "-halt-on-error", "-no-shell-escape", tex_path.name],
                cwd=tex_path.parent,
                text=True,
                capture_output=True,
                check=False,
                timeout=30,
            )
        except subprocess.TimeoutExpired:
            raise RuntimeError("Tempo limite ao gerar PDF; o arquivo .tex foi preservado.") from None
        pdf_path = tex_path.with_suffix(".pdf")
        if result.returncode != 0 or not pdf_path.exists():
            raise RuntimeError("Falha ao gerar PDF; o arquivo .tex foi preservado.")
        return pdf_path

    def _content(self, data: ResumeTemplateData) -> str:
        parts = [self._header(data)]
        if data.professional_summary:
            parts.append(self._section("Resumo Profissional", escape_latex(data.professional_summary)))
        skills = [
            rf"\textbf{{{escape_latex(group.category)}:}} {', '.join(escape_latex(item) for item in group.items)} \\\\"
            for group in data.technical_skills
            if group.category and group.items
        ]
        if skills:
            parts.append(self._section("Habilidades Técnicas", "\n".join(skills)))
        experiences = [self._experience(experience) for experience in data.experiences]
        if experiences:
            parts.append(self._section("Experiência Profissional", "\n".join(experiences)))
        projects = [self._project(project) for project in data.projects]
        if projects:
            parts.append(self._section("Projetos", "\n".join(projects)))
        education = [self._education(item) for item in data.education]
        if education:
            parts.append(self._section("Educação", "\n".join(education)))
        return "\n".join(parts)

    def _header(self, data: ResumeTemplateData) -> str:
        personal = data.personal
        contacts = []
        if personal.city:
            location = personal.city if not personal.state else f"{personal.city} -- {personal.state}"
            contacts.append(escape_latex(location))
        for value in (personal.phone, personal.email, personal.linkedin, personal.github, personal.portfolio):
            if value:
                contacts.append(escape_latex(value))
        lines = [r"\begin{center}", rf"{{\fontsize{{17}}{{18}}\selectfont\textbf{{{escape_latex(personal.name)}}}}}"]
        if personal.headline:
            lines.append(rf"\\[1pt]\textbf{{{escape_latex(personal.headline)}}}")
        if contacts:
            lines.append(r"\\[1pt]" + r" \textbullet\ ".join(contacts))
        lines.append(r"\end{center}")
        return "\n".join(lines)

    @staticmethod
    def _section(title: str, content: str) -> str:
        return rf"\section{{{title}}}" + "\n" + content

    def _experience(self, item: ResumeExperience) -> str:
        heading = self._entry_heading(item.company, item.location)
        subheading = self._entry_sub(item.position, item.period)
        return "\n".join(part for part in (heading, subheading, self._bullets(item.bullets)) if part)

    def _project(self, item: ResumeProject) -> str:
        heading = self._entry_heading(item.name, item.context)
        technologies = r" \textbullet\ ".join(escape_latex(value) for value in item.technologies)
        subheading = rf"\entrysub{{{technologies}}}{{}}" if technologies else ""
        return "\n".join(part for part in (heading, subheading, self._bullets(item.bullets)) if part)

    def _education(self, item: ResumeEducation) -> str:
        return "\n".join((self._entry_heading(item.institution, item.location), self._entry_sub(item.course, item.period)))

    @staticmethod
    def _entry_heading(left: str, right: str | None) -> str:
        return rf"\entryheading{{{escape_latex(left)}}}{{{escape_latex(right or '')}}}"

    @staticmethod
    def _entry_sub(left: str, right: str) -> str:
        return rf"\entrysub{{{escape_latex(left)}}}{{{escape_latex(right)}}}"

    @staticmethod
    def _bullets(bullets: list[str]) -> str:
        if not bullets:
            return ""
        items = "\n".join(rf"\item {escape_latex(bullet)}" for bullet in bullets if bullet)
        return "\\begin{itemize}\n" + items + "\n\\end{itemize}" if items else ""

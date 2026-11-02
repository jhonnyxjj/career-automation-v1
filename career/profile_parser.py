from __future__ import annotations

import re
from io import BytesIO
from pathlib import Path

from pypdf import PdfReader
from pypdf.errors import PdfReadError

from .config import TECH_CATALOG
from .models import CandidateProfile, ResumeEducation, ResumeExperience, ResumePersonalDetails, ResumeProject, TechnicalSkillGroup
from .normalizer import extract_technologies, normalized_text


SECTION_NAMES = {
    "resumo": "summary", "resumo profissional": "summary", "summary": "summary", "professional summary": "summary",
    "experiencia": "experience", "experiencia profissional": "experience", "professional experience": "experience", "experience": "experience",
    "projetos": "projects", "projects": "projects",
    "formacao": "education", "formacao academica": "education", "education": "education",
    "habilidades": "skills", "habilidades tecnicas": "skills", "skills": "skills", "technical skills": "skills",
}


def _sections(lines: list[str]) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    current = None
    for line in lines:
        heading = normalized_text(line.rstrip(":"))
        if heading in SECTION_NAMES:
            current = SECTION_NAMES[heading]
            sections.setdefault(current, [])
        elif current:
            sections[current].append(line)
    return sections


def _structured_entries(lines: list[str], kind: str) -> list:
    entries = []
    current = None
    for line in lines:
        if line.startswith(("- ", "• ", "* ")):
            if current is not None and kind != "education":
                current.bullets.append(line[2:].strip())
            continue
        fields = [part.strip() for part in re.split(r"\||\s+[–—]\s+", line)]
        current = None
        if kind == "experience" and len(fields) == 3 and all(fields):
            current = ResumeExperience(position=fields[0], company=fields[1], period=fields[2])
        elif kind == "education" and len(fields) == 3 and all(fields):
            current = ResumeEducation(course=fields[0], institution=fields[1], period=fields[2])
        elif kind == "projects" and len(fields) in {1, 2} and fields[0]:
            current = ResumeProject(name=fields[0], context=fields[1] if len(fields) == 2 and fields[1] else None)
        if current is not None:
            entries.append(current)
    return entries


def parse_candidate_profile(pdf_content: bytes, profile_id: str, original_path: Path) -> CandidateProfile:
    try:
        reader = PdfReader(BytesIO(pdf_content))
        if reader.is_encrypted:
            raise ValueError("O PDF está protegido por senha. Envie uma cópia desbloqueada.")
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    except PdfReadError as error:
        raise ValueError("Não foi possível ler o PDF enviado.") from error
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        raise ValueError("Não foi possível extrair texto do PDF.")

    name = lines[0][:120]
    headline = None
    if len(lines) > 1:
        candidate = lines[1]
        if re.search(r"[A-Za-zÀ-ÿ]", candidate) and "@" not in candidate and "http" not in candidate.lower() and not re.search(r"\d{5,}", candidate) and not re.match(r"(?:cidade|uf)\s*:", candidate, re.I) and normalized_text(candidate.rstrip(":")) not in SECTION_NAMES:
            headline = candidate[:160]
    email_match = re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", text)
    phone = None
    for line in lines:
        if normalized_text(line.rstrip(":")) in SECTION_NAMES:
            break
        contact_line = re.sub(r"https?://[^\s<>]+|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", " ", line, flags=re.I)
        for match in re.finditer(r"\+?\d[\d ().-]{7,}\d", contact_line):
            if 10 <= len(re.sub(r"\D", "", match.group())) <= 15:
                phone = match.group()
                break
        if phone:
            break
    urls = re.findall(r"https?://[^\s<>]+", text)
    city = state = None
    for line in lines:
        if normalized_text(line.rstrip(":")) in SECTION_NAMES:
            break
        city_match = re.fullmatch(r"cidade\s*:\s*([^|,;]+)", line, re.I)
        state_match = re.fullmatch(r"uf\s*:\s*([A-Za-z]{2})", line, re.I)
        if city_match and city is None:
            city = city_match.group(1).strip()
        if state_match and state is None:
            state = state_match.group(1).upper()
    linkedin = next((url.rstrip(".,;") for url in urls if re.search(r"^https?://(?:www\.)?linkedin\.com/", url, re.I)), None)
    github = next((url.rstrip(".,;") for url in urls if re.search(r"^https?://(?:www\.)?github\.com/", url, re.I)), None)
    portfolio_match = re.search(r"\bportf[oó]lio\s*:\s*(https?://[^\s<>]+)", text, re.I)
    portfolio = portfolio_match.group(1).rstrip(".,;") if portfolio_match else None
    sections = _sections(lines)
    skills_by_category: dict[str, list[str]] = {}
    labels = {"language": "Linguagens", "framework": "Frameworks", "database": "Banco de Dados", "cloud_devops": "Cloud & DevOps", "complementary": "Ferramentas"}
    for technology in extract_technologies(text):
        category = TECH_CATALOG[technology][0]
        skills_by_category.setdefault(labels[category], []).append(technology)

    return CandidateProfile(
        id=profile_id,
        original_resume_path=str(original_path),
        personal=ResumePersonalDetails(name=name, headline=headline, city=city, state=state, email=email_match.group() if email_match else None, phone=phone, linkedin=linkedin, github=github, portfolio=portfolio),
        professional_summary=" ".join(sections.get("summary", [])) or None,
        technical_skills=[TechnicalSkillGroup(category=category, items=items) for category, items in skills_by_category.items()],
        experiences=_structured_entries(sections.get("experience", []), "experience"),
        projects=_structured_entries(sections.get("projects", []), "projects"),
        education=_structured_entries(sections.get("education", []), "education"),
    )

from __future__ import annotations

import re
from io import BytesIO
from pathlib import Path

from pypdf import PdfReader
from pypdf.errors import PdfReadError

from .config import TECH_CATALOG
from .models import CandidateProfile, ResumePersonalDetails, TechnicalSkillGroup
from .normalizer import extract_technologies


def parse_candidate_profile(pdf_content: bytes, profile_id: str, original_path: Path) -> CandidateProfile:
    try:
        reader = PdfReader(BytesIO(pdf_content))
    except PdfReadError as error:
        raise ValueError("Não foi possível ler o PDF enviado.") from error
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        raise ValueError("Não foi possível extrair texto do PDF.")

    name = lines[0][:120]
    headline = next((line[:160] for line in lines[1:5] if "@" not in line and not re.search(r"\d{5,}", line)), None)
    email_match = re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", text)
    phone_match = re.search(r"(?:\+?\d[\d\s().-]{7,}\d)", text)
    skills_by_category: dict[str, list[str]] = {}
    labels = {"language": "Linguagens", "framework": "Frameworks", "database": "Banco de Dados", "cloud_devops": "Cloud & DevOps", "complementary": "Ferramentas"}
    for technology in extract_technologies(text):
        category = TECH_CATALOG[technology][0]
        skills_by_category.setdefault(labels[category], []).append(technology)

    return CandidateProfile(
        id=profile_id,
        original_resume_path=str(original_path),
        personal=ResumePersonalDetails(name=name, headline=headline, email=email_match.group() if email_match else None, phone=phone_match.group() if phone_match else None),
        technical_skills=[TechnicalSkillGroup(category=category, items=items) for category, items in skills_by_category.items()],
    )

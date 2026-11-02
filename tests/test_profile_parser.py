from pathlib import Path

import pytest

from career.profile_parser import parse_candidate_profile


def test_extracts_structured_sections_without_inventing_fields(monkeypatch):
    text = """Pessoa Exemplo
Desenvolvedora Backend
pessoa@example.com
https://linkedin.com/in/exemplo
https://github.com/exemplo
Resumo Profissional
Desenvolvedora com foco em APIs.
Experiência Profissional
Desenvolvedora | Empresa Exemplo | 2022–2024
- Criou APIs em TypeScript.
Projetos
Projeto Exemplo | Aplicação web
- Criou testes.
Formação
Computação | Universidade Exemplo | 2020–2024
Habilidades Técnicas
Node.js PostgreSQL
"""
    class Page:
        def extract_text(self):
            return text
    class Reader:
        is_encrypted = False
        def __init__(self, _):
            self.pages = [Page()]
    monkeypatch.setattr("career.profile_parser.PdfReader", Reader)
    profile = parse_candidate_profile(b"fake", "id", Path("original.pdf"))
    assert profile.personal.linkedin == "https://linkedin.com/in/exemplo"
    assert profile.personal.github == "https://github.com/exemplo"
    assert profile.professional_summary == "Desenvolvedora com foco em APIs."
    assert profile.experiences[0].company == "Empresa Exemplo"
    assert profile.experiences[0].bullets == ["Criou APIs em TypeScript."]
    assert profile.projects[0].name == "Projeto Exemplo"
    assert profile.education[0].institution == "Universidade Exemplo"


def test_empty_extracted_pdf_is_rejected(monkeypatch):
    class Reader:
        is_encrypted = False
        def __init__(self, _):
            self.pages = []
    monkeypatch.setattr("career.profile_parser.PdfReader", Reader)
    with pytest.raises(ValueError, match="extrair texto"):
        parse_candidate_profile(b"fake", "id", Path("original.pdf"))


def test_page_number_is_not_a_headline(monkeypatch):
    class Page:
        def extract_text(self):
            return "Pessoa Exemplo\n1"
    class Reader:
        is_encrypted = False
        def __init__(self, _):
            self.pages = [Page()]
    monkeypatch.setattr("career.profile_parser.PdfReader", Reader)
    assert parse_candidate_profile(b"fake", "id", Path("original.pdf")).personal.headline is None


def test_education_dates_are_not_extracted_as_a_phone_number(monkeypatch):
    class Page:
        def extract_text(self):
            return "Pessoa Exemplo\nFormação\nComputação | Universidade | 2020-2024"
    class Reader:
        is_encrypted = False
        def __init__(self, _):
            self.pages = [Page()]
    monkeypatch.setattr("career.profile_parser.PdfReader", Reader)
    assert parse_candidate_profile(b"fake", "id", Path("original.pdf")).personal.phone is None


def test_extracts_formatted_phone_number(monkeypatch):
    class Page:
        def extract_text(self):
            return "Pessoa Exemplo\n+55 (21) 99999-1234\nFormação\nComputação | Universidade | 2020-2024"
    class Reader:
        is_encrypted = False
        def __init__(self, _):
            self.pages = [Page()]
    monkeypatch.setattr("career.profile_parser.PdfReader", Reader)
    assert parse_candidate_profile(b"fake", "id", Path("original.pdf")).personal.phone == "+55 (21) 99999-1234"


def test_extracts_only_explicitly_labeled_portfolio(monkeypatch):
    class Page:
        def extract_text(self):
            return "Pessoa Exemplo\nPortfólio: https://example.com/pessoa\nProjetos\nProjeto | https://example.org/projeto"
    class Reader:
        is_encrypted = False
        def __init__(self, _):
            self.pages = [Page()]
    monkeypatch.setattr("career.profile_parser.PdfReader", Reader)
    assert parse_candidate_profile(b"fake", "id", Path("original.pdf")).personal.portfolio == "https://example.com/pessoa"


def test_project_link_is_not_invented_as_portfolio(monkeypatch):
    class Page:
        def extract_text(self):
            return "Pessoa Exemplo\nProjetos\nProjeto | https://example.org/projeto"
    class Reader:
        is_encrypted = False
        def __init__(self, _):
            self.pages = [Page()]
    monkeypatch.setattr("career.profile_parser.PdfReader", Reader)
    assert parse_candidate_profile(b"fake", "id", Path("original.pdf")).personal.portfolio is None

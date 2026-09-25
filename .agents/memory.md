## 2026-09-25 — Pipeline de currículos

- Contexto: o projeto ganhou currículos originais e adaptados sem acoplar o matching ao LaTeX.
- Decisão: `CandidateProfile` é a fonte da verdade; `ResumeTailoringService` apenas prioriza conteúdo existente; `LaTeXRenderer` recebe exclusivamente `ResumeTemplateData` e faz escape centralizado.
- Evidência: `career/models.py`, `career/tailoring.py`, `career/latex.py` e testes de currículo.

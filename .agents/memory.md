## 2026-09-25 — Pipeline de currículos

- Contexto: o projeto ganhou currículos originais e adaptados sem acoplar o matching ao LaTeX.
- Decisão: `CandidateProfile` é a fonte da verdade; `ResumeTailoringService` apenas prioriza conteúdo existente; `LaTeXRenderer` recebe exclusivamente `ResumeTemplateData` e faz escape centralizado.
- Evidência: `career/models.py`, `career/tailoring.py`, `career/latex.py` e testes de currículo.

## 2026-09-26 — Fontes de vagas e posts

- Contexto: a busca passou a incluir PrimeiraVagaTech, Remotinho e posts de recrutadores.
- Decisão: coletar somente fontes públicas permitidas; para LinkedIn e plataformas sem API/parceria autorizada, o usuário importa o texto e URLs manualmente. Não automatizar login, navegador ou candidatura.
- Evidência: `career/sources/primeiravagatech.py`, `career/sources/remotinho.py`, `career/api.py` e `README.md`.

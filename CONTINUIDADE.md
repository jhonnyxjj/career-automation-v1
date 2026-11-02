# Continuidade — Career Automation V1.1

Data: 2026-11-01. Último commit válido observado: `2a74073 fix(resume): clarify PDF generation failures`. O branch está à frente do remoto; não houve push. `.agents/memory.md` contém alteração preexistente não commitada e deve ser preservada.

A retomada verificou a especificação do Notion e preservou os trabalhos anteriores. Foram adicionados commits pequenos para correções LaTeX, isolamento Docker, fontes manuais, filtros e ranking, explicações do score, recuperação de vagas, CI, documentação e testes E2E. Os dados pessoais em `.data/` não foram usados nos testes. O Compose E2E usa portas 13000/18000 e volume próprio; os testes utilizam um PDF fictício.

Verificações observadas: 84 testes Python passaram em container isolado, com um aviso de depreciação de Starlette/httpx; Ruff (E9,F63,F7,F82) passou. Lint, typecheck e 5 testes web passaram. O build e a inicialização pelo Compose passaram; API ficou healthy e web respondeu HTTP 200. Os dois testes Playwright passaram no Compose E2E, incluindo upload, confirmação e refresh, importação, acompanhamento, PDF/TeX, falha de rede simulada, PDF inválido e apresentação simulada de PDF indisponível. Reinício do container e restauração foram verificados manualmente em ambiente isolado. A CI do GitHub ainda não executou porque não houve publicação remota.

Pendências: validar a CI remota quando houver autorização para publicar; ampliar cobertura E2E para falha real/timeout de fonte e indisponibilidade real de LaTeX através da interface; revisar o tratamento de localidades ambíguas e preferências de cidade; considerar a penalidade para experiência de 2–3 anos prevista no Notion; tornar o build Python reproduzível com o lockfile; validar operação e backup em instalação limpa. Ver limitações em `docs/operacao.md`. Não declarar V1.1 concluída enquanto os critérios de aceite ainda não estiverem comprovados.

Próxima ação: revisar `git status`, preservar a alteração preexistente e validar os fluxos restantes em ambiente isolado. Consultar a especificação em https://app.notion.com/p/40a27698d6818190bb0dc7eec7c7d489 e manter os commits locais incrementais, sem push automático.

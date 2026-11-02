# Career Automation V1.1 — auditoria e continuidade

Atualizado em 2026-11-02. Este é um retrato para continuidade, não uma declaração de que a V1.1 está pronta. A [especificação vigente](https://app.notion.com/p/40a27698d6818190bb0dc7eec7c7d489) e o [quadro de tarefas](https://app.notion.com/p/5cefab2cb8044bf2be9474a0baea3fff) são as fontes de requisitos e status. O histórico detalhado de validações está em [auditoria-v1.1.md](auditoria-v1.1.md).

## Estado de Git e cuidados

- Repositório: `jhonnyxjj/career-automation-v1`, branch `main`. O último commit publicado é `a408ad1`; o último commit de código validado antes desta atualização é `3517082`. Confira `git status -sb` e `git log -10 --oneline` antes de continuar, pois há commits locais posteriores ao push.
- `.agents/memory.md` e `CONTINUIDADE.md` eram alterações preexistentes; durante a execução, passaram a constar no commit `a4566bc`, criado fora destas entregas. Preserve seu conteúdo e confira o estado atual antes de editar.
- Não versionar `.data/`, currículos, `.env`, credenciais ou backups. Não fazer push sem nova instrução. A aplicação principal pode estar em execução com imagens anteriores; um commit ou push não atualiza automaticamente seus containers.
- A [CI do push `a408ad1`](https://github.com/jhonnyxjj/career-automation-v1/actions/runs/41459341087) terminou com sucesso: backend, frontend, Compose e navegador passaram. Os commits locais posteriores ainda não foram executados na CI remota.

## O que existe e o que falta

| Fase | Implementado e evidências | Pendente ou limitado |
| --- | --- | --- |
| P0 — baseline | Bun/lockfile, Docker Compose local, regras em `AGENTS.md` e verificação do estado anterior. No último registro confirmado, Notion: Concluído. | Imagens base e pacotes de sistema não são fixados por digest/versão; preservar trabalho preexistente. |
| P1 — filtros e rede | Filtros de modalidade/região/senioridade, distinção de desconhecidos, score explicável, timeouts e isolamento em loopback. Testes de API integram fonte com falha e deduplicação; navegador testa apresentação de falha/revisão. Notion foi confirmado como Concluído após validação. | Classificação geográfica e senioridade são heurísticas; resposta de busca no E2E de interface é simulada. Links manuais não são buscados pelo backend; a validação não resolve DNS. |
| P2 — perfil e currículo | Upload, edição, confirmação, restauração, versões originais e adaptação validada com fatos confirmados; PDF/TeX e recuperação de falha real testados no navegador. Concluído no Notion após validação local de `f44a102`. | Extração estruturada reconhece formatos delimitados por `\|` e travessão com espaços; PDFs em colunas, digitalizados ou ambíguos podem exigir correção manual. Não há OCR. |
| P4 — persistência e candidaturas | Perfil, buscas, vagas e funil persistidos; refresh, reinício real da API e restauração de backup sintético em API/volume separado foram validados, incluindo histórico e idempotência. Concluído no Notion. | Backup é manual, sem exportação na interface ou mesclagem; trava de concorrência é de um processo. Dados pessoais não foram usados nos testes. |
| P3 — plataformas | Seis origens manuais testadas com exemplos sintéticos distintos; deduplicação entre portais validada em API e navegador; fontes complementares preservadas e falha parcial/429 testada. Concluído no Notion. | Sem ingestão automática de alertas ou retry/backoff de 429; disponibilidade real das fontes não foi exaustivamente verificada. Vagas idênticas com URLs e fingerprints diferentes podem não ser deduplicadas. Gupy/ProgramaThor automáticas aparecem como indisponíveis, não como coleta ativa. |
| P5 — qualidade | Um clone Git limpo do commit `139207d` passou em 209 testes Python, mypy nos 34 arquivos, Ruff, sintaxe, lint/typecheck e cinco testes frontend, build/health Compose, quatro E2E normais e um E2E separado de falha real. O log de acesso não registrou marcador sintético. Notion: Em Andamento. | A CI remota verde cobre apenas `a408ad1`; executar CI dos commits locais após publicação autorizada. Mypy usa configuração padrão, não estrita. Logs de erro permanecem ativos e podem conter dados sensíveis. |

P2, P4 e P3 foram confirmadas como Concluídas no Notion após as validações de 2026-11-02. P5 foi iniciada e permanece Em Andamento.

## Fluxos críticos

- **A — currículo:** upload, edição, confirmação e refresh passaram em navegador em clone limpo; teste de API preserva dois PDFs ao trocar e rejeita PDF inválido sem perder o perfil. Layouts complexos e PDFs digitalizados continuam limitados.
- **B — descoberta:** integração com fonte sintética verifica normalização, deduplicação, filtros, score, revisão e falha parcial; interface de busca usa resposta simulada no E2E. Faltam exemplos representativos por portal e observação das fontes reais permitidas.
- **C — candidatura:** status, favorita e nota sobreviveram ao refresh e ao reinício real da API; backup sintético restaurado em volume e API separados preservou esses dados, URL, score e histórico.
- **D — currículo adaptado:** E2E validou geração e download de PDF e `.tex`; teste especial validou falha real do compilador com download do `.tex`. A seleção de conteúdo usa perfil confirmado; revisar fatos e dados ausentes em novos casos.
- **E — falhas:** há testes de rede/timeout, PDF inválido, protegido, truncado e vazio, fonte com erro e falha LaTeX. Não se conclui que todos os cenários ou toda a interface foram exaustivamente testados.

## Ordem de retomada

1. Reconfirmar status e critérios no Notion; reler `AGENTS.md`, `web/AGENTS.md`, histórico e alterações locais. Observar a CI de futuros commits quando houver publicação autorizada.
2. Manter as limitações de **P2** documentadas: PDFs em colunas/digitalizados podem exigir correção manual e não há OCR. Reabrir a tarefa se uma regressão for reproduzida.
3. Manter as limitações de **P4** documentadas; reinício de API e restauração de backup foram validados com volumes sintéticos. Preservar `.data/` do usuário; não introduzir PostgreSQL por padrão.
4. Manter as limitações de **P3** documentadas e reabrir em caso de regressão. Sem login, bypass, scraping não autorizado ou candidatura automática.
5. Concluir **P5**: revisar casos de exceção e privacidade ainda não demonstrados e verificar a CI remota dos commits locais quando a publicação for autorizada. Os fluxos testados passaram em clone limpo, com fontes sintéticas; a CI publicada não cobre o novo mypy. Atualizar o Notion com evidências, sem concluir fases por mera existência de código.

## Comandos para retomar

Na raiz, confira o estado sem alterar dados:

```sh
git status -sb
git log -10 --oneline
git diff --stat
docker compose config
```

Para executar a aplicação local, use `docker compose up --build` e acesse `http://localhost:3000`. O volume principal `./.data` pode conter dados pessoais; não o use para testes destrutivos e faça backup privado antes de qualquer recuperação.

Verificações do projeto, conforme `AGENTS.md`:

```sh
uv sync --locked
uv run pytest
uv run --locked --no-sync mypy career
ruff check --select E9,F63,F7,F82 career tests
cd web
bun install --frozen-lockfile
bun run lint
bunx next typegen
bunx tsc --noEmit
bun test
bun run build
```

Os testes Playwright e o teste de falha real de LaTeX usam Compose e volume separados; siga os comandos de [operação](operacao.md#testes-de-navegador). Não os aponte para a instalação principal. Ao alterar código: escrever/verificar o cenário, executar os testes pertinentes, revisar o diff, fazer stage apenas dos arquivos da entrega e criar commit local Conventional Commit. Registrar resultado e próximo passo no Notion e nesta auditoria.

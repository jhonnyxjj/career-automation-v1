# Career Automation V1.1 — auditoria e continuidade

Atualizado em 2026-11-02. Este é um retrato para continuidade, não uma declaração de que a V1.1 está pronta. A [especificação vigente](https://app.notion.com/p/40a27698d6818190bb0dc7eec7c7d489) e o [quadro de tarefas](https://app.notion.com/p/5cefab2cb8044bf2be9474a0baea3fff) são as fontes de requisitos e status. O histórico detalhado de validações está em [auditoria-v1.1.md](auditoria-v1.1.md).

## Estado de Git e cuidados

- Repositório: `jhonnyxjj/career-automation-v1`, branch `main`. O último commit publicado é `a408ad1`; o último commit de código validado antes deste relatório é `f44a102`. Confira `git status -sb` e `git log -10 --oneline` antes de continuar, pois há commits locais posteriores ao push.
- `.agents/memory.md` estava modificada e `CONTINUIDADE.md` estava não rastreado antes deste trabalho. São alterações preexistentes: leia e preserve, sem reset, sobrescrita ou inclusão acidental em commits.
- Não versionar `.data/`, currículos, `.env`, credenciais ou backups. Não fazer push sem nova instrução. A aplicação principal pode estar em execução com imagens anteriores; um commit ou push não atualiza automaticamente seus containers.
- A [CI do push `a408ad1`](https://github.com/jhonnyxjj/career-automation-v1/actions/runs/41459341087) terminou com sucesso: backend, frontend, Compose e navegador passaram. Os commits locais posteriores ainda não foram executados na CI remota.

## O que existe e o que falta

| Fase | Implementado e evidências | Pendente ou limitado |
| --- | --- | --- |
| P0 — baseline | Bun/lockfile, Docker Compose local, regras em `AGENTS.md` e verificação do estado anterior. No último registro confirmado, Notion: Concluído. | Imagens base e pacotes de sistema não são fixados por digest/versão; preservar trabalho preexistente. |
| P1 — filtros e rede | Filtros de modalidade/região/senioridade, distinção de desconhecidos, score explicável, timeouts e isolamento em loopback. Testes de API integram fonte com falha e deduplicação; navegador testa apresentação de falha/revisão. Notion foi confirmado como Concluído após validação. | Classificação geográfica e senioridade são heurísticas; resposta de busca no E2E de interface é simulada. Links manuais não são buscados pelo backend; a validação não resolve DNS. |
| P2 — perfil e currículo | Upload, edição, confirmação, restauração, versões originais e adaptação validada com fatos confirmados; PDF/TeX e recuperação de falha real testados no navegador. Concluído no Notion após validação local de `f44a102`. | Extração estruturada reconhece formatos delimitados por `\|` e travessão com espaços; PDFs em colunas, digitalizados ou ambíguos podem exigir correção manual. Não há OCR. |
| P4 — persistência e candidaturas | Perfil, buscas, vagas e funil persistidos; refresh, reinício real da API e restauração de backup sintético em API/volume separado foram validados, incluindo histórico e idempotência. Concluído no Notion. | Backup é manual, sem exportação na interface ou mesclagem; trava de concorrência é de um processo. Dados pessoais não foram usados nos testes. |
| P3 — plataformas | Importação manual reconhece LinkedIn, Indeed, Gupy, Vagas.com.br, ProgramaThor e InfoJobs pelo mesmo pipeline; Greenhouse, Lever, PrimeiraVagaTech e Remotinho têm conectores no código. Gupy/ProgramaThor como fontes automáticas padrão aparecem como indisponíveis, não como coleta ativa. | Fixtures atuais de importação usam dados sintéticos comuns; ampliar exemplos representativos das seis origens e verificar 429/limites/retries quando aplicáveis. Não há integração automática de alertas. Verificar disponibilidade real das fontes sem login ou scraping proibido. Último status Notion observado: Backlog; reconfirme. |
| P5 — qualidade | Há pytest, lint focado, testes frontend, Playwright, CI, Docker e documentação. No estado `f44a102`, 198 testes Python e Ruff passaram; três testes normais de navegador passaram e o teste especial de falha real passou separadamente. | Testar commits locais em nova CI quando houver publicação autorizada. Typecheck Python não está configurado; faltam cenários reais de erro e validação integral dos fluxos críticos em ambiente limpo. Último status Notion observado: Backlog; reconfirme. |

P2 foi confirmada como Concluída no Notion após a revalidação em 2026-11-02. Os demais estados identificados como última observação devem ser reconfirmados antes de alteração.

## Fluxos críticos

- **A — currículo:** upload, edição, confirmação e refresh passaram em navegador; teste de API preserva dois PDFs ao trocar e rejeita PDF inválido sem perder o perfil. Falta ampliar PDFs/layouts e comprovar o conjunto completo em ambiente limpo.
- **B — descoberta:** integração com fonte sintética verifica normalização, deduplicação, filtros, score, revisão e falha parcial; interface de busca usa resposta simulada no E2E. Faltam exemplos representativos por portal e observação das fontes reais permitidas.
- **C — candidatura:** status, favorita e nota sobrevivem ao refresh no navegador; teste API usa novo cliente. Falta reforçar restauração após reinício de containers e backup restaurado.
- **D — currículo adaptado:** E2E validou geração e download de PDF e `.tex`; teste especial validou falha real do compilador com download do `.tex`. A seleção de conteúdo usa perfil confirmado; revisar fatos e dados ausentes em novos casos.
- **E — falhas:** há testes de rede/timeout, PDF inválido, protegido, truncado e vazio, fonte com erro e falha LaTeX. Não se conclui que todos os cenários ou toda a interface foram exaustivamente testados.

## Ordem de retomada

1. Reconfirmar status e critérios no Notion; reler `AGENTS.md`, `web/AGENTS.md`, histórico e alterações locais. Observar a CI de futuros commits quando houver publicação autorizada.
2. Manter as limitações de **P2** documentadas: PDFs em colunas/digitalizados podem exigir correção manual e não há OCR. Reabrir a tarefa se uma regressão for reproduzida.
3. Manter as limitações de **P4** documentadas; reinício de API e restauração de backup foram validados com volumes sintéticos. Preservar `.data/` do usuário; não introduzir PostgreSQL por padrão.
4. Continuar **P3**: ampliar fixtures realistas para as seis origens manuais, deduplicação, erros/429 e relatórios; preservar conectores públicos existentes. Sem login, bypass, scraping não autorizado ou candidatura automática.
5. Consolidar **P5**: repetir fluxos A–E, lint, tipos, testes, build, Compose e CI; revisar exceções, dados pessoais, README e operação em ambiente limpo. Atualizar o Notion com evidências, sem concluir fases por mera existência de código.

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
uv run pytest
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

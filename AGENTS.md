# Career Automation — instruções do projeto

## Fontes e início de trabalho

- A especificação vigente é https://app.notion.com/p/40a27698d6818190bb0dc7eec7c7d489 e o quadro é https://app.notion.com/p/5cefab2cb8044bf2be9474a0baea3fff. Consulte-os quando acessíveis e confira o código antes de presumir status; links, por si só, não concedem acesso.
- Antes de alterar arquivos, inspecione `git status`, histórico e diffs relevantes, leia `.agents/memory.md`, `CONTINUIDADE.md` quando existir, `docs/auditoria-v1.1.md` e as instruções mais específicas do diretório, inclusive `web/AGENTS.md`. Compare datas e evidências se os relatórios divergirem. Preserve alterações preexistentes e dados pessoais.
- Compare tarefas e critérios de aceite com implementação, testes e resultados observados. Atualize status no Notion somente quando seus critérios estiverem comprovados. Se o Notion estiver indisponível, registre evidências e pendências localmente para sincronização posterior.
- Escolha o próximo incremento pelo backlog aprovado, prioridades e dependências. Para trabalho de várias etapas, apresente plano conciso com verificação e riscos; siga autonomamente quando houver autorização do usuário. Peça aprovação para operações destrutivas, deploy público, mudanças significativas de arquitetura ou quando exigida por instrução aplicável.

## Arquitetura, produto e segurança

- Preserve Python/FastAPI, Next.js/TypeScript, Docker Compose local e persistência privada em `.data/`. Não acrescente tecnologia principal ou altere a arquitetura sem justificativa e aprovação quando necessária.
- Não automatize login, CAPTCHA, scraping não autorizado ou candidaturas. As seis origens prioritárias são LinkedIn, Indeed, Gupy, Vagas.com.br, ProgramaThor e InfoJobs por importação manual; não prometa coleta automática sem integração autorizada. Preserve os conectores públicos existentes.
- O perfil confirmado é a fonte dos fatos do currículo. Não invente experiência ou habilidades; preserve os PDFs originais e o `.tex` quando o PDF falhar. Distinga informação desconhecida de informação negativa.
- Não versione `.data/`, `.env`, credenciais, currículos pessoais, backups ou artefatos temporários. Não exponha serviços locais publicamente. Execute testes com dados sintéticos e isolamento dos dados reais.

## Entregas e verificação

- Faça alterações mínimas e alinhadas aos padrões existentes; evite refatorações sem relação com a tarefa. Acrescente testes relevantes para regressões e falhas.
- Faça commits locais pequenos e independentes em Conventional Commits, após executar as verificações relevantes; faça stage somente dos arquivos da entrega. Não reescreva histórico nem faça push sem pedido explícito.
- Use as skills `anti-deception-verification` e, para trabalho médio/grande, `staff-engineer-review`. Antes de commit com impacto de segurança, entrada, dependências ou deploy, use `security-audit-quick`. Respeite as demais instruções e skills aplicáveis.
- Relate somente verificações executadas e observadas. Ao fim de cada etapa, registre commit, testes, limitações e próxima ação. Se houver interrupção, atualize um relatório de continuidade sem dados sensíveis. Não declare a versão pronta sem validar os fluxos críticos e critérios vigentes.

## Comandos de verificação

- Backend: `uv run pytest`; sintaxe: `python -m compileall -q career`.
- Lint Python focado: `ruff check --select E9,F63,F7,F82 career tests` (Ruff 0.17.3). Typecheck Python: não configurado.
- Frontend: `cd web && bun run lint && bunx next typegen && bunx tsc --noEmit && bun test`; build: `cd web && bun run build`.
- Compose: `docker compose config` e, quando aplicável, `docker compose up --build` com verificação de saúde.
- E2E: use o Compose isolado e os comandos em `docs/operacao.md`; nunca aponte esses testes para dados pessoais.

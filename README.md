# Career Automation

Automação local para identificar um perfil a partir de um currículo PDF, buscar vagas públicas compatíveis e gerar versões adaptadas do currículo sem inventar informações.

```text
Web Next.js -> API FastAPI -> fontes de vagas / matching / LaTeX-PDF
```

## Rodar localmente

Requer Docker Desktop. Em uma única janela de terminal:

```powershell
docker compose up --build
```

Abra `http://localhost:3000`. A API fica em `http://localhost:8000`, e a documentação interativa está em `http://localhost:8000/docs`.

Os currículos e resultados ficam somente em `.data/` no seu computador. A busca de vagas requer internet; identificação do perfil e geração de currículo usam os dados locais já armazenados.

Para encerrar:

```powershell
docker compose down
```

## Fluxo

1. Envie um PDF de até 10 MB.
2. Revise o perfil e tecnologias identificados.
3. Selecione filtros e busque vagas nas fontes configuradas.
4. Gere um currículo adaptado para uma vaga e baixe `.tex` ou PDF.

O PDF original nunca é sobrescrito. Cada currículo adaptado é associado a um perfil original e a uma vaga. Dados externos passam por escape centralizado antes de entrar no LaTeX.

## Configuração de fontes

Opcionalmente, crie `.data/settings.json`:

```json
{
  "greenhouse_boards": [{"id": "cloudflare", "company": "Cloudflare"}],
  "lever_sites": [{"id": "netlify", "company": "Netlify"}]
}
```

## Fontes de vagas

Greenhouse, Lever, PrimeiraVagaTech e Remotinho são consultados por suas fontes públicas.
Para LinkedIn (incluindo posts de recrutadores), Indeed, Gupy, ProgramaThor, Sólides Vagas,
Vagas.com.br, InfoJobs, Glassdoor e outras fontes sem integração autorizada, use **Importar vaga ou post**: cole a
descrição, a URL da origem e, se existir, a URL de candidatura. A aplicação não acessa contas,
não automatiza navegadores e não envia candidaturas em seu nome.

Para arquitetura, backup, privacidade e limitações, consulte [operação](docs/operacao.md).

## Publicação

Esta versão é local e não inclui autenticação. Não a exponha publicamente ainda: antes de publicar, adicione autenticação, armazenamento privado persistente e variáveis de ambiente de produção.

## Comandos de verificação

- Lint web: `cd web; bun run lint`
- Typecheck web: `cd web; bunx tsc --noEmit`
- Build web: `cd web; bun run build`
- Testes web: `cd web; bun test`
- Testes API/domínio: `uv run pytest`
- Verificação de sintaxe Python: `python -m compileall -q career`
- Lint Python (erros críticos; requer Ruff 0.17.3): `ruff check --select E9,F63,F7,F82 career tests`
- Typecheck Python: não configurado
- Compose: `docker compose config`
- E2E de navegador: veja [operação](docs/operacao.md#testes-de-navegador)

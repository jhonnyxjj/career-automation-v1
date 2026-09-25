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

## Publicação

Esta versão é local e não inclui autenticação. Não a exponha publicamente ainda: antes de publicar, adicione autenticação, armazenamento privado persistente e variáveis de ambiente de produção.

## Comandos de verificação

- Lint web: `cd web; npm.cmd run lint`
- Build web: `cd web; npm.cmd run build`
- Testes API/domínio: `uv run pytest`
- Compose: `docker compose config`

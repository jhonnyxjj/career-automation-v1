# Auditoria do backlog V1.1

Auditoria em 2026-11-01, sobre o commit publicado `2a74073` e a correção local `59816a1`. Fonte: [especificação](https://app.notion.com/p/40a27698d6818190bb0dc7eec7c7d489) e [quadro](https://app.notion.com/p/5cefab2cb8044bf2be9474a0baea3fff). As seis tarefas estavam em Backlog quando consultadas. Os estados abaixo são avaliações locais, não alterações automáticas do Notion.

| Fase | Evidências | Pontos de aceite ainda pendentes ou insuficientemente verificados |
| --- | --- | --- |
| [P0](https://app.notion.com/p/40a27698d68181d5a598e74cc0372402) | Árvore e histórico inspecionados; Bun com lockfile, Docker e exclusões presentes. Backend e builds foram executados sem apagar alterações preexistentes. | O build Python instala dependências sem usar `uv.lock`; a reprodução integral em ambiente limpo ainda precisa ser comprovada. |
| [P1](https://app.notion.com/p/40a27698d681815aa949f26a5649e7e3) | Filtros de modalidade/região, score versionado, tratamento de desconhecidos e timeout existem; testes de filtros e rede passaram. URLs manuais são armazenadas, não requisitadas pela API. Portas ficam em loopback. | Falhas e combinações de rede/filtros não foram exaustivamente verificadas no navegador; localidades ambíguas e preferências precisam de revisão. |
| [P2](https://app.notion.com/p/40a27698d68181c3b3f8e003c3db74f0) | Editor, confirmação, restauração, originais preservados e fallback `.tex` implementados; testes de parser, persistência e LaTeX passaram; fluxo sintético passou em navegador. | Extração é heurística: experiências e formação estruturadas exigem formato específico e cidade/UF e portfólio não são extraídos. Validar PDFs variados e falha real de compilação na interface. |
| [P3](https://app.notion.com/p/40a27698d681815b8195d3ff9ae09bbc) | Seis origens aceitam importação manual pelo mesmo pipeline; testes parametrizados, deduplicação e falha parcial de fonte passaram. Greenhouse, Lever e fontes complementares existem. | Fixtures usam conteúdo sintético comum, não exemplos representativos por portal; respostas 429 e limites/retries não estão demonstrados. Integração automática de alertas não existe. |
| [P4](https://app.notion.com/p/40a27698d68181a7a647f34a3eb9a5df) | Perfis, vagas, buscas e funil persistidos em arquivos; testes de escrita/idempotência e E2E de refresh passaram. Reinício foi testado manualmente em volume sintético. | Backup manual está documentado, mas recuperação de backup em instalação limpa ainda não foi demonstrada; não há exportação na interface. |
| [P5](https://app.notion.com/p/40a27698d6818179b116c6a309813cfd) | CI, testes backend/frontend/E2E, Docker e documentação existem. Nesta auditoria: 84 testes Python, lint Python focado, lint/typecheck e cinco testes web passaram. | A [CI publicada](https://github.com/jhonnyxjj/career-automation-v1/actions/runs/41320842396) falhou no typecheck frontend; backend, Compose e E2E passaram. A correção `59816a1` passou em cópia limpa local, mas ainda não executou no GitHub. Typecheck Python e alguns cenários reais de falha E2E seguem pendentes. |

## Rastreabilidade e prioridade

1. Preservar `.agents/memory.md` e `CONTINUIDADE.md` preexistentes. Não fazer push sem pedido explícito.
2. A correção de CI deve ser verificada remotamente após publicação autorizada; antes disso, não registrar P5 como concluída.
3. Resolver as lacunas de perfil, filtros e persistência na ordem de dependências do plano; validar cada entrega isoladamente. O score ainda não penaliza requisitos de 2–3 anos e a localização presencial não oferece preferências de cidade configuráveis.
4. Atualizar o status de uma tarefa no Notion somente após comprovar todos os critérios pertinentes. Na auditoria inicial nenhuma fase havia sido alterada: a tabela registra o estado observado naquele momento.

## Continuação — 2026-11-01

- **P0 concluída no Notion:** status confirmado por releitura após verificar preservação da árvore, 84 testes Python, frontend e builds; o E2E passou novamente com a imagem Python do lockfile. O commit `0a63f8a` aplica `uv.lock` à imagem e à CI. Imagem base e pacotes do sistema ainda não têm fixação por digest/versão; isso limita a reprodutibilidade bit a bit.
- **Regras permanentes:** `73ad749` adicionou `AGENTS.md` na raiz, preservando as instruções específicas do frontend.
- **CI:** `59816a1` gera tipos do Next.js antes do typecheck. A falha foi reproduzida em cópia limpa e o comando corrigido passou nessa cópia. A execução remota falhou antes da correção; a nova versão ainda não foi publicada nem verificada no GitHub.
- **P1:** `8fb89c0` corrige a aceitação de Niterói como cidade do Rio em vagas presenciais/híbridas. O teste falhou antes e a suíte com dependências travadas passou depois: 93 testes. Continuam pendentes a revisão de localidades ambíguas e a validação completa dos critérios de P1.
- **Próxima ação:** continuar P1 pelos critérios do Notion e validar os demais casos sem ler ou alterar dados pessoais; após P1, seguir P2 e P4 conforme dependências. P1–P5 permanecem em Backlog no Notion até a comprovação dos respectivos aceites.

### Incremento posterior de P1

- `1e9e1c5` introduz a versão 2 do score, com penalidade de até cinco pontos para menções reconhecidas de 2–3 anos de experiência. Os pontos são explicados na interface; frases negadas e intervalos fora do escopo não recebem essa penalidade nos testes. A detecção é heurística e não cobre todas as redações.
- Verificações: 105 testes Python com dependências travadas, Ruff focado, lint/typecheck e cinco testes frontend; dois E2E passaram, incluindo a explicação da penalidade. O E2E foi construído antes do último refinamento do reconhecimento de negação; esse refinamento foi coberto pela suíte Python posterior.
- P1 permanece em Backlog até revisar os casos ambíguos de região e validar integralmente os demais critérios. A próxima tarefa é continuar essa revisão e então avançar ao parser de P2. A CI ainda precisa ser observada remotamente após publicação autorizada.

- **Filtro de área:** `2cdfb4f` corrige um falso positivo em que título explicitamente frontend era aceito por mencionar backend na descrição. O cenário falhou antes da correção; após ela, a suíte com lockfile passou com 108 testes e o lint Python focado passou. Próximo passo: revisar ambiguidades restantes de P1 e, em seguida, o parser de P2.

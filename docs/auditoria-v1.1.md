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

### Retomada mais recente — 2026-11-02

- `9274f78` impede que localizações que excluem o Brasil com “outside” ou “fora” sejam aceitas por conter seu nome; restrições na descrição ficam para revisão. O cenário falhou antes e passou depois. Suíte final: 112 testes Python e lint Ruff focado aprovados; houve um aviso de depreciação Starlette/httpx.
- **Próxima ação:** continuar P1 revisando outras expressões e combinações geográficas, sem presumir elegibilidade; depois seguir P2 e P4. P1–P5 continuam em Backlog no Notion porque seus critérios ainda não foram integralmente comprovados.
- **CI e publicação:** o último run remoto do commit `2a74073` falhou no typecheck frontend; `59816a1` corrige o problema e passou em cópia limpa local, mas os commits posteriores ainda não foram enviados nem executados no GitHub. Não fazer push sem solicitação explícita.
- **Estado local:** preservar a modificação anterior em `.agents/memory.md` e o arquivo não rastreado `CONTINUIDADE.md`. Este registro é mais recente que aquele relatório. Os serviços principais em execução ainda correspondem à imagem anterior; as mudanças novas foram verificadas em containers e dados sintéticos isolados.

### Incremento P1 — região não informada

- `bf95f8d` encaminha para revisão vagas cuja localização informa somente modalidade remota, sem presumir país nem classificá-las como região proibida. Os cenários “Remote”, “Remoto”, “Home office” e “Work from home” falharam antes da correção; foram adicionados casos de pontuação, texto vazio e integração da busca.
- Verificações: 117 testes Python e Ruff focado passaram; após acrescentar dois casos adicionais, os 28 testes direcionados de filtros/busca passaram. A CI remota continua reprovada no commit anterior e as correções locais ainda não foram publicadas.
- Próxima ação: continuar P1 pela detecção de requisitos sênior explícitos e cenários de falha; P1 permanece em Backlog até comprovar os demais critérios.

### Incremento P1 — requisitos sênior explícitos

- `ff2bc34` identifica formulações diretas de exigência de experiência sênior em português e inglês; menções a colegas/mentores e frases negadas não são tratadas como exigências nos testes. Os casos de exigência falharam antes da correção.
- Verificações: 128 testes Python e Ruff focado passaram com dependências travadas; o teste emitiu aviso de depreciação Starlette/httpx. A identificação é heurística e não cobre todas as formas de expressar requisitos sênior, staff, lead ou arquitetura.
- Próxima ação: continuar P1 com as ambiguidades de senioridade e região, validar os critérios restantes e atualizar seu status no Notion somente após o aceite. Nenhum push foi feito; a CI remota da correção continua pendente.

### Incremento P1 — data de publicação

- `b90e535` deixa a data de publicação do Greenhouse desconhecida em vez de usar `updated_at`. O teste reproduziu o erro antes da mudança; a suíte com lockfile passou depois com 129 testes, e o lint Ruff focado passou. A listagem pública não apresentou data de primeira publicação no exemplo da documentação oficial; não foi adicionada uma consulta por vaga.
- Próxima ação: concluir a revisão de P1, incluindo elegibilidade, erros de rede e persistência dos resultados, antes de alterar o status da fase. A CI remota da correção continua pendente de publicação autorizada.

### Incremento P1 — requisitos staff, lead e arquitetura

- `3c25286` amplia o filtro de requisitos explícitos para staff, lead e arquiteto, preservando nos testes as menções a colegas. Três requisitos eram aceitos antes da mudança e foram corrigidos.
- Verificações: 134 testes Python e lint Ruff focado passaram com dependências travadas. A identificação continua heurística e não reconhece todas as formulações ou contextos possíveis.
- Próxima ação: concluir a revisão de P1, em especial riscos de falsa classificação e tratamento de erros de interface; não alterar o status no Notion até comprovar os critérios da fase. A CI remota das alterações locais ainda depende de push solicitado pelo usuário.

### Incremento P1 — links de importação

- `bacf6bd` rejeita `localhost`, nomes `.local`, endereços privados literais e formas numéricas alternativas nos links manuais de origem e candidatura. O backend não busca esses links; a validação não resolve DNS e não garante que um domínio aponte para endereço público.
- Verificações: 163 testes Python com lockfile e Ruff focado passaram; testes cobrem os dois campos, IPv4/IPv6, formas alternativas e resposta HTTP 422. A suíte emitiu aviso de depreciação Starlette/httpx.
- Próxima ação: revisar os critérios restantes de P1 e a apresentação de falhas no navegador; sincronizar o status no Notion apenas após comprovar o aceite. Nenhum push foi feito.

### Incremento P1 — localidades não reconhecidas

- `fbce015` encaminha localidades não reconhecidas para revisão, incluindo no fluxo de busca, e evita identificar siglas de região dentro de outras palavras. Localidades reconhecidas fora das preferências continuam rejeitadas; a lista de regiões ainda é limitada e restrições geográficas complexas precisam de revisão.
- Verificações: 169 testes Python com lockfile e Ruff focado passaram; houve aviso de depreciação Starlette/httpx. Antes deste incremento, dois testes E2E passaram no Compose isolado com dados sintéticos; eles não foram repetidos após a alteração do filtro.
- Próxima ação: revisar restrições geográficas ambíguas e os demais critérios de P1; depois seguir P2, P4, P3 e P5. P1–P5 ainda não têm aceite comprovado. O último run remoto conhecido da CI falhou e as correções locais não foram publicadas. Preservar `.agents/memory.md` e `CONTINUIDADE.md` preexistentes.

### Incremento P1 — restrições sobre outras regiões

- `bc12367` encaminha para revisão restrições geográficas que não mencionam nenhuma região específica aceita pelo perfil. Vagas globais que excluem Canadá ou Estados Unidos eram rejeitadas para um perfil brasileiro; os dois testes reproduziram a falha e passaram após a correção.
- Verificações: 171 testes Python com lockfile e Ruff focado passaram; permanece o aviso de depreciação Starlette/httpx. Restrições compostas que mencionam também uma região aceita ainda exigem revisão; não presumir que o reconhecimento heurístico esgota todas as combinações.
- Próxima ação: revisar as restrições compostas e os demais critérios de P1, antes de prosseguir para P2, P4, P3 e P5. Não declarar as fases concluídas sem comprovação; não publicar automaticamente.

### Incremento P1 — restrições compostas

- `3654926` encaminha restrições compostas e exclusões com múltiplas regiões preferidas para revisão; mantém a rejeição dos casos simples reconhecidos que excluem o Brasil quando ele é a única região específica desejada. Quatro cenários falharam antes da correção.
- Verificações: 175 testes Python com lockfile e Ruff focado passaram; permanece aviso de depreciação Starlette/httpx. O reconhecimento é deliberadamente conservador e não interpreta todas as redações geográficas; a fase P1 ainda requer validação integral na interface.
- Próxima ação: verificar os critérios restantes de P1 e avançar para P2, P4, P3 e P5; preservar alterações preexistentes, sem push automático. Último run remoto da CI conhecido continua reprovado.

### Incremento P2 — telefone extraído do currículo

- `545b67a` evita interpretar períodos de formação como telefone: busca números plausíveis no cabeçalho, antes das seções, sem concatenar linhas. O erro com `2020-2024` foi reproduzido antes da correção; um telefone brasileiro formatado também foi testado.
- Verificações: 177 testes Python com lockfile e Ruff focado passaram; permanece aviso de depreciação Starlette/httpx. Números fora do cabeçalho, na mesma linha de e-mail/link ou com menos de dez dígitos podem exigir correção manual. Os testes usam texto sintético e extração de PDF simulada, não PDFs variados.
- Próxima ação: ampliar e validar a extração de P2 com currículos sintéticos representativos, além de concluir a validação da P1; seguir P4, P3 e P5. A CI remota continua pendente de publicação autorizada. Preservar `.agents/memory.md` e `CONTINUIDADE.md` preexistentes.

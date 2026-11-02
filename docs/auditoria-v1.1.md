# Auditoria do backlog V1.1

Auditoria em 2026-11-01, sobre o commit publicado `2a74073` e a correção local `59816a1`. Fonte: [especificação](https://app.notion.com/p/40a27698d6818190bb0dc7eec7c7d489) e [quadro](https://app.notion.com/p/5cefab2cb8044bf2be9474a0baea3fff). As seis tarefas estavam em Backlog quando consultadas. Os estados abaixo são avaliações locais, não alterações automáticas do Notion.

| Fase | Evidências | Pontos de aceite ainda pendentes ou insuficientemente verificados |
| --- | --- | --- |
| [P0](https://app.notion.com/p/40a27698d68181d5a598e74cc0372402) | Árvore e histórico inspecionados; Bun com lockfile, Docker e exclusões presentes. Backend e builds foram executados sem apagar alterações preexistentes. | O build Python instala dependências sem usar `uv.lock`; a reprodução integral em ambiente limpo ainda precisa ser comprovada. |
| [P1](https://app.notion.com/p/40a27698d681815aa949f26a5649e7e3) | Filtros de modalidade/região, score versionado, tratamento de desconhecidos e timeout existem; testes de filtros e rede passaram. URLs manuais são armazenadas, não requisitadas pela API. Portas ficam em loopback. | Falhas e combinações de rede/filtros não foram exaustivamente verificadas no navegador; localidades ambíguas e preferências precisam de revisão. |
| [P2](https://app.notion.com/p/40a27698d68181c3b3f8e003c3db74f0) | Editor, confirmação, restauração, originais preservados e fallback `.tex` implementados; testes de parser, persistência e LaTeX passaram; fluxo sintético passou em navegador. | Extração é heurística: experiências e formação estruturadas exigem formato específico, cidade/UF e portfólio exigem rótulos explícitos. Validar PDFs variados e falha real de compilação na interface. |
| [P3](https://app.notion.com/p/40a27698d681815b8195d3ff9ae09bbc) | Seis origens aceitam importação manual pelo mesmo pipeline; testes parametrizados, deduplicação e falha parcial de fonte passaram. Greenhouse, Lever e fontes complementares existem. | Fixtures usam conteúdo sintético comum, não exemplos representativos por portal; respostas 429 e limites/retries não estão demonstrados. Integração automática de alertas não existe. |
| [P4](https://app.notion.com/p/40a27698d68181a7a647f34a3eb9a5df) | Perfis, vagas, buscas e funil persistidos em arquivos; testes de escrita/idempotência e E2E de refresh passaram. Reinício foi testado manualmente em volume sintético. | Backup manual está documentado, mas recuperação de backup em instalação limpa ainda não foi demonstrada; não há exportação na interface. |
| [P5](https://app.notion.com/p/40a27698d6818179b116c6a309813cfd) | CI, testes backend/frontend/E2E, Docker e documentação existem. A [CI do commit publicado `da4ab48`](https://github.com/jhonnyxjj/career-automation-v1/actions/runs/41454961547) passou em backend, frontend, Compose e navegador. | Os commits locais posteriores ainda não executaram na CI remota. Typecheck Python e alguns cenários reais de falha E2E seguem pendentes. |

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

### Incremento P2 — PDF protegido por senha

- `690cc86` rejeita PDFs criptografados com resposta HTTP 422 e orientação para enviar uma cópia desbloqueada. Um teste de integração gerou um PDF protegido sintético e comprovou que o arquivo rejeitado é removido; antes da mudança, uma exceção escapava da API e o upload permanecia no disco. Erros `PdfReadError` durante a extração de páginas também são convertidos em erro de leitura.
- Verificações: 178 testes Python com lockfile e Ruff focado passaram; permanece aviso de depreciação Starlette/httpx. O teste cobre a API, não a apresentação de erro no navegador; PDFs protegidos, inclusive os que podem ter senha vazia, precisam ser desbloqueados antes do envio.
- Próxima ação: validar os demais cenários da P2 com PDFs sintéticos representativos e as falhas na interface; continuar a validação de P1 e as fases P4, P3 e P5. Não atualizar o Notion para concluído sem aceite, nem fazer push automático. Preservar `.agents/memory.md` e `CONTINUIDADE.md` preexistentes.

### Incremento P2 — portfólio explicitamente identificado

- `8ce8c44` extrai URLs HTTP(S) rotuladas como `Portfólio:` ou `Portfolio:` para o campo existente no editor; não confunde um link de projeto com portfólio. O cenário positivo falhou antes da implementação e os dois cenários passaram depois.
- Verificações: 180 testes Python com lockfile e Ruff focado passaram. A primeira tentativa da suíte falhou antes de executar os testes por timeout ao baixar `hatchling` do PyPI; uma nova tentativa completou. O parser foi testado com texto sintético e leitor simulado; URLs sem rótulo ou sem protocolo não são inferidas.
- Próxima ação: validar com PDFs sintéticos reais e continuar os critérios pendentes da P2, além da validação integral de P1; seguir P4, P3 e P5. O último run remoto conhecido da CI falhou; nenhum push foi feito. Preservar `.agents/memory.md` e `CONTINUIDADE.md` preexistentes.

### Incremento P2 — integração de portfólio com PDF real sintético

- `c18657e` testa o upload de um PDF sintético com texto real e confirma que a API retorna o portfólio extraído, sem simular o leitor de PDF. O teste não cobre layouts variados nem links embutidos como anotações.
- Verificações: 181 testes Python com lockfile e Ruff focado passaram; permanece aviso de depreciação Starlette/httpx.
- Próxima ação: continuar P2 pelos formatos de extração ainda não suportados e falhas de compilação na interface; validar P1, P4, P3 e P5 conforme backlog. O último run remoto conhecido da CI falhou; sem push automático. Preservar `.agents/memory.md` e `CONTINUIDADE.md` preexistentes.

### Validação de integração P1 — 2026-11-02

- `e96db1e` acrescenta teste de integração da API com PDF e fontes sintéticas: deduplicação, score, exclusão de sênior e híbrido, revisão de localização desconhecida e relatório de falha parcial foram verificados juntos. A suíte inteira passou com 182 testes Python e Ruff focado; houve aviso de depreciação Starlette/httpx.
- `4400f5a` verifica no navegador a apresentação de localização desconhecida e falha parcial de fonte, incluindo retorno do botão ao estado utilizável. A resposta de busca nesse teste é simulada; o processamento real da busca é coberto separadamente pelo teste de API. Os três testes Playwright passaram no Compose isolado reconstruído, assim como lint e typecheck frontend.
- O teste de navegador existente também verificou upload, confirmação, restauração, importação, acompanhamento e geração PDF/TeX, além de falha de rede e PDF inválido. As fontes reais e todas as combinações geográficas não foram verificadas nesta rodada; a integração completa do navegador com resultados reais de fontes não foi demonstrada.
- A consulta ao Notion falhou por erro de transporte. Não foi possível reconfirmar os critérios ou sincronizar o status; P1 não deve ser marcada como concluída com base somente nesses testes. Próxima ação: reconciliar os critérios quando o Notion voltar e continuar P2, P4, P3 e P5. O último run remoto conhecido da CI falhou; não fazer push automaticamente. Preservar `.agents/memory.md` e `CONTINUIDADE.md` preexistentes.

### Publicação e incremento P2 — contatos na mesma linha

- Por solicitação explícita, `main` foi enviada ao GitHub até `da4ab48`. A execução [CI 41454961547](https://github.com/jhonnyxjj/career-automation-v1/actions/runs/41454961547) foi observada em andamento; consulta posterior falhou por indisponibilidade de rede, portanto o resultado ainda não foi confirmado.
- `932472b` corrige a limitação registrada na etapa de telefone: números na mesma linha que e-mail ou URL são identificados após remover esses endereços da análise, sem tratar seus dígitos como telefone. O cenário positivo falhou antes da correção; a suíte com lockfile passou depois com 184 testes, e Ruff focado passou. Persiste aviso de depreciação Starlette/httpx.
- Próxima ação: conferir o resultado da CI publicada e continuar P2, P4, P3 e P5, reconciliando P1 com o Notion quando acessível. O novo commit é local e posterior ao push; preservar `.agents/memory.md` e `CONTINUIDADE.md` preexistentes.

### CI publicada e incremento P2 — localização explícita

- A [CI 41454961547](https://github.com/jhonnyxjj/career-automation-v1/actions/runs/41454961547) terminou com sucesso no commit publicado `da4ab48`: backend, frontend, Compose e browser E2E passaram. Os commits locais posteriores não foram executados por essa CI.
- `dbcf2bc` extrai cidade e UF somente de campos explicitamente rotulados no cabeçalho e não interpreta cidade de experiência profissional como cidade pessoal. Também evita usar a linha de cidade/UF como título profissional. O caso positivo falhou antes da alteração; após a correção, 186 testes Python com lockfile e Ruff focado passaram. O teste usa texto sintético com leitor simulado; outros formatos permanecem manuais. Houve aviso de depreciação Starlette/httpx.
- Próxima ação: validar PDFs sintéticos adicionais e falhas da P2 na interface; reconciliar P1 com o Notion e seguir P4, P3 e P5. Os commits posteriores a `da4ab48` ainda são locais; preservar `.agents/memory.md` e `CONTINUIDADE.md` preexistentes.

### Aceite P1 e reconciliação com Notion — 2026-11-02

- A especificação e o quadro foram consultados; após erro de transporte inicial, uma nova tentativa funcionou. P0 consta como concluída; P1 foi atualizada para **Concluído** e confirmada por releitura após revalidação dos critérios. P2 consta como Em Andamento; P4, P3 e P5 foram observadas em Backlog.
- No estado local `a078d64`, passaram 186 testes Python, cinco testes frontend, lint/typecheck frontend e três Playwright no Compose isolado reconstruído; `docker compose config` confirmou bind em `127.0.0.1`. CI remota do commit anterior `da4ab48` passou; commits locais posteriores não estão nessa CI.
- Limitações registradas no Notion: reconhecimento geográfico e senioridade heurístico, resposta de busca simulada no teste de navegador e nenhum teste exaustivo de fontes reais; o backend não requisita URLs manuais e não resolve DNS na validação desses links. Aviso Starlette/httpx permanece.
- Próxima ação: P2, especialmente PDFs textuais variados, experiência/projetos/formação, confirmação e preservação do original, e falha de LaTeX; depois P4, P3 e P5. Não fazer push automático; preservar `.agents/memory.md` e `CONTINUIDADE.md` preexistentes.

### P2 — integração com PDF e falha de compilação

- `eb9d165` testa um PDF textual sintético real com resumo, experiência, projeto e formação no formato estruturado existente, confirmação, leitura do perfil atual e preservação byte a byte do original. Não valida todos os layouts.
- `b7458f9` executa o `pdflatex` real com template inválido e confirma a preservação do `.tex` e dos metadados. O teste é ignorado em ambientes sem compilador. A falha real ainda não foi verificada pela interface; o E2E atual simula a resposta sem PDF.
- A suíte completa passou com 188 testes Python e Ruff focado; permanece aviso de depreciação Starlette/httpx. Os incrementos e limites foram registrados na tarefa P2 do Notion, que continua Em Andamento.
- Próxima ação: validar a interface com falha real de compilação e PDFs variados, concluir os critérios restantes da P2 e seguir P4, P3 e P5. Commits posteriores a `da4ab48` são locais; não fazer push automático. Preservar `.agents/memory.md` e `CONTINUIDADE.md` preexistentes.

### P2 — falha real de PDF no navegador

- `a9d71fa` adiciona E2E com template inválido montado exclusivamente no Compose isolado. O `pdflatex` estava instalado; o navegador recebeu a resposta real de falha e baixou o `.tex` com os dados sintéticos. O procedimento está em `docs/operacao.md` e o teste especial é desativado na suíte normal.
- Verificações: o E2E especial passou; após restaurar o template normal, três testes Playwright passaram e o teste especial foi ignorado como esperado. Lint, typecheck e validação do Compose especial passaram. A etapa foi registrada no Notion; P2 permanece Em Andamento.
- Próxima ação: testar PDFs de layouts variados e preservação de versões, revisar o aceite restante da P2 e continuar P4, P3 e P5. Não fazer push automático; preservar `.agents/memory.md` e `CONTINUIDADE.md` preexistentes.

### P2 — preservação ao trocar currículo

- `9fead3d` valida pela API a troca entre dois PDFs sintéticos: o perfil anterior permanece ativo até confirmar o novo; ambos os perfis e originais continuam disponíveis, com comparação byte a byte. A restauração foi verificada em novo cliente de teste, sem reiniciar containers.
- Verificações: 189 testes Python e Ruff focado passaram; permanece aviso de depreciação Starlette/httpx. O resultado foi registrado no Notion; P2 permanece Em Andamento.
- Próxima ação: validar PDFs de layouts variados e os critérios restantes de P2; depois P4, P3 e P5. Commits posteriores a `da4ab48` continuam locais; preservar `.agents/memory.md` e `CONTINUIDADE.md` preexistentes e não fazer push automático.

### P2 — PDFs ilegíveis, multipágina e separadores

- `b764cba` comprova que PDFs sintéticos truncado e sem texto são rejeitados sem modificar o perfil confirmado ou o PDF original; `90bf78d` valida extração em PDF textual sintético linear de três páginas. Esses testes não abrangem layouts em colunas ou PDFs digitalizados.
- `090c49d` acrescenta suporte a travessões com espaços entre campos de experiência, projeto e formação, além da barra vertical existente. O teste reproduziu a ausência de experiência antes da correção e verifica que campos incompletos não são inventados; o leitor de PDF é simulado nesse cenário. Datas com travessões cercados de espaços e layouts complexos podem exigir correção manual.
- Verificações finais: 194 testes Python com lockfile e Ruff focado passaram; permanece aviso de depreciação Starlette/httpx. As entregas e limitações foram registradas na tarefa P2 do Notion, que permanece Em Andamento.
- Próxima ação: validar o novo separador em PDF textual sintético real e revisar os critérios restantes da P2, depois seguir P4, P3 e P5. Commits posteriores a `da4ab48` são locais; preservar `.agents/memory.md` e `CONTINUIDADE.md` preexistentes e não fazer push automático.

### Publicação, validação e continuidade — 2026-11-02

- A pedido do usuário, foi feito push até `a408ad1`. A [CI correspondente](https://github.com/jhonnyxjj/career-automation-v1/actions/runs/41459341087) terminou com sucesso: backend, frontend, Compose e navegador passaram.
- `b0e395b` valida o separador por travessão no upload de PDF textual sintético real, sem simular o leitor. A suíte passou com 195 testes Python e Ruff focado; o commit é posterior ao push. O progresso foi registrado na tarefa P2 do Notion, que continua Em Andamento.
- O relatório [continuidade-v1.1.md](continuidade-v1.1.md) reúne funcionalidades existentes, fases pendentes, testes, limitações, commits e comandos para retomada. Próxima ação: continuar P2; depois P4, P3 e P5. Preservar `.agents/memory.md` e `CONTINUIDADE.md` preexistentes; não fazer novo push automaticamente.

### Aceite P2 — 2026-11-02

- P2 foi marcada como Concluída no Notion e confirmada por releitura após validar edição e restauração de experiência, projeto e formação no navegador (`95a1157`), preservação de versões (`9fead3d`), dados confirmados no currículo adaptado (`1fea272`), timeout e recuperação de `.tex` em falha real do compilador (`a9d71fa`).
- `76b1d45` corrige confusão entre Java e JavaScript na ordenação de experiências; `f44a102` evita atribuir atividades de experiência incompleta à anterior. Os erros foram reproduzidos antes das correções. No estado `f44a102`, 198 testes Python e Ruff focado passaram; cinco testes frontend, lint, typecheck, três E2E normais e o E2E separado de falha real passaram, com Compose isolado reconstruído.
- Limitações: extração heurística requer revisão, não há OCR, e PDFs em colunas ou com ordenação/separadores ambíguos podem não ser extraídos corretamente; atividades não associáveis são omitidas. O aviso Starlette/httpx permanece. A CI verde do commit publicado `a408ad1` não cobre commits locais posteriores.
- Próxima ação: P4 — verificar restart real de containers, restauração de backup isolado e integridade/idempotência; depois P3 e P5. Não fazer push automático; preservar `.agents/memory.md` e `CONTINUIDADE.md` preexistentes.

### Aceite P4 — 2026-11-02

- P4 foi marcada como Concluída no Notion e confirmada por releitura. Após gerar perfil e candidatura sintéticos no navegador, reiniciou-se a API do Compose isolado e foram confirmados perfil, vaga, situação, favorita e nota por HTTP.
- Um backup tar do volume sintético foi restaurado em volume vazio e lido por uma API isolada separada. Perfil, vaga, URL, score, situação, nota, favorita e histórico foram verificados; atualização repetida preservou histórico e timestamp. Testes existentes cobrem persistência de buscas, idempotência e corrupção de JSON.
- Limitações: backup é manual, sem exportação na interface ou mesclagem; a trava de concorrência é de um processo. Os volumes `career-v11-synthetic-backup-20261102` e `career-v11-synthetic-restore-20261102` contêm somente dados de teste e foram preservados. Dados pessoais não foram usados.
- Próxima ação: P3 — fixtures representativas das seis fontes manuais, deduplicação, falhas e limites de rede; depois P5. Não fazer push automático; preservar `.agents/memory.md` e `CONTINUIDADE.md` preexistentes.

### Aceite P3 — 2026-11-02

- P3 foi marcada como Concluída no Notion e confirmada por releitura. `af2bd8c` testa seis exemplos sintéticos de importação manual; `cfa07d2` verifica deduplicação entre portais sem perder dados da candidatura; `3379035` cobre falha parcial por HTTP 429. As fontes automáticas complementares continuam no código.
- `f5d29b2` corrige a identificação de “vaga remota”; `7cdc2b4` corrige o fuso de publicação no PrimeiraVagaTech; `caac1f5` corrige a duplicação da mesma vaga na lista de resultados. Os erros foram reproduzidos antes das correções.
- Verificações: 208 testes Python e Ruff focado passaram; quatro testes Playwright, lint, typecheck e cinco testes frontend passaram com Compose isolado reconstruído. O teste especial de falha LaTeX foi ignorado na suíte normal e passou separadamente antes das alterações de P3.
- Limitações: fixtures são sintéticas; disponibilidade real das fontes não foi exaustivamente verificada. Não há ingestão automática de alertas; 429 é reportado sem retry/backoff. Vagas idênticas com URLs e fingerprints diferentes podem não ser deduplicadas. A CI remota de `a408ad1` não cobre os commits locais posteriores.
- Próxima ação: P5 — consolidar testes, build, segurança e documentação; não declarar a V1.1 pronta sem validar os fluxos críticos. Não fazer push automático; preservar `.agents/memory.md` e `CONTINUIDADE.md` preexistentes.

### Consolidação P5 — 2026-11-02

- `78d81d0` adiciona `.env.example` e documenta/configura as variáveis locais; `docker compose config` passou com padrões e alternativas, mantendo portas em loopback, e o build passou. `73f8dfe` corrige HTML sem `href` no Remotinho; `17e56ac` inclui mypy 1.18.2 no lockfile e na CI e corrige anotações. O mypy é executado com configuração padrão, não estrita.
- Em cópia isolada dos arquivos versionados em `17e56ac` e volume novo, passaram instalação com lockfiles, build/health Compose, 209 testes Python, mypy nos 34 arquivos, Ruff e sintaxe, lint/typecheck e cinco testes frontend, quatro E2E normais e um E2E separado de falha real de LaTeX. A cópia excluiu arquivos pessoais e não é um checkout Git integral.
- Os logs coletados após recriar o container não continham três marcadores sintéticos de nome/nota; isso não demonstra ausência absoluta de PII em todos os caminhos. O aviso Starlette/httpx permanece. A CI remota verde de `a408ad1` não cobre os commits locais posteriores, inclusive o novo mypy; P5 permanece Em Andamento no Notion.
- Próxima ação: revisar exceções e privacidade remanescentes e validar a CI dos commits locais quando houver publicação autorizada. Os arquivos `.agents/memory.md` e `CONTINUIDADE.md`, antes preexistentes sem commit, passaram a constar no commit `a4566bc` criado fora destas entregas; preservá-los e conferir o estado atual.

### P5 — privacidade de logs de acesso

- `3517082` desativa o log de acesso HTTP do Uvicorn no container e adiciona uma verificação com marcador sintético à CI. Antes da correção, um parâmetro fictício apareceu no log; depois da reconstrução isolada, a API respondeu e o marcador não apareceu. Quatro E2E normais passaram após a mudança; o teste especial de falha LaTeX foi ignorado nessa execução.
- Logs de inicialização e erros continuam ativos e podem conter informações sensíveis; o teste não prova ausência absoluta de PII. A verificação nova na CI ainda não foi executada remotamente.
- P5 permanece Em Andamento no Notion. Próxima ação: revisar erros e privacidade remanescentes e confirmar a CI dos commits locais após publicação autorizada. Não fazer push automático.

### P5 — validação em checkout Git limpo

- Um clone Git limpo do commit `139207d`, com volume Docker sintético novo, passou na instalação por lockfiles, build/health Compose, 209 testes Python, mypy nos 34 arquivos, Ruff, compilação de sintaxe, lint/typecheck e cinco testes frontend, quatro E2E normais e o E2E separado de falha real de LaTeX.
- Uma requisição com marcador sintético respondeu sem registrar o marcador no log de acesso. Isso não prova ausência de PII em todas as exceções; logs de inicialização e erro continuam potencialmente sensíveis. Permanece aviso de depreciação Starlette/httpx.
- O resultado foi registrado no Notion. P5 permanece Em Andamento: a CI verde publicada cobre `a408ad1`, não os commits locais posteriores. Próxima ação: revisar tratamento de erros e observar a CI remota do estado local após publicação autorizada; não fazer push automaticamente.

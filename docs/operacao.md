# Operação e privacidade

## Arquitetura

A interface Next.js chama a API FastAPI no navegador. A API extrai texto de PDFs com pypdf, normaliza vagas, aplica filtros e calcula um score determinístico. O perfil confirmado é a única fonte para o conteúdo do currículo adaptado. O LaTeX escapa os dados e `pdflatex` tem limite de 30 segundos; se a compilação falhar, o `.tex` continua disponível.

Os dados ficam em `.data/`, montado no container da API. Perfis confirmados e acompanhamento usam gravação atômica de arquivos; o acompanhamento é protegido contra concorrência dentro do processo da API. Esta instalação destina-se a um único usuário local e não deve ser exposta à internet. Não há autenticação nem coordenação entre múltiplos processos da API.

## Fluxo e fontes

Envie um PDF textual, corrija e confirme o perfil. A extração é heurística e PDFs digitalizados ou com disposição complexa podem produzir dados ausentes ou incorretos. Revise sempre antes de confirmar. A troca de currículo cria uma nova versão original; os arquivos anteriores não são sobrescritos.

Busque nas fontes públicas configuradas ou importe uma vaga preenchendo os campos e colando o texto que você consultou. LinkedIn, Indeed, Gupy, Vagas.com.br, ProgramaThor e InfoJobs são origens manuais; não há coleta automática nesses portais nem envio automático de candidaturas. Greenhouse, Lever, PrimeiraVagaTech e Remotinho são conectores públicos complementares; disponibilidade e resultados variam. Consulte o relatório de fontes após a busca.

No acompanhamento, marque favorito, escolha a situação, preencha observações e salve. Uma vaga persistida pode ser reaberta para consultar detalhes e adaptar o currículo. O score representa apenas sinais identificados, não uma probabilidade de contratação. Novos resultados incluem uma explicação versionada; pontuações já armazenadas não são recalculadas automaticamente ao atualizar o aplicativo ou o perfil. Busque ou importe novamente para obter um novo cálculo.

## Backup e restauração

Com a aplicação parada (`docker compose down`), copie a pasta `.data/` inteira para um local privado e protegido. Ela contém currículos, perfis, vagas e observações pessoais. Para restaurar, pare a aplicação e substitua `.data/` somente após guardar uma cópia dos dados atuais; reinicie com `docker compose up --build`. O aplicativo não possui exportação pela interface nem mesclagem automática de backups.

## Segurança e resolução de problemas

O Compose publica as portas apenas em `127.0.0.1`. Não compartilhe `.data/`, currículos, arquivos `.env` ou backups. Fontes externas recebem solicitações de busca; textos colados na importação manual não são enviados automaticamente ao site de origem. Não há OCR, integração com e-mail, login automatizado ou candidatura automática.

- Se a interface não abrir, confira `docker compose ps` e `docker compose logs` sem compartilhar logs que possam conter dados pessoais.
- Se o PDF não for gerado, baixe o `.tex` e verifique a instalação LaTeX. O original permanece preservado.
- Se uma fonte falhar, consulte o relatório; as demais podem retornar resultados independentemente.
- Se a API não estiver acessível, confira `http://localhost:8000/health` e reinicie o Compose.

## Limitações conhecidas

A ordenação prioriza estágio e júnior, depois o score e, em caso de empate, datas mais recentes. O score não aplica penalidade específica a anos de experiência. Localidades presenciais/híbridas por cidade ainda não possuem todas as regras da especificação. Vagas plenas sem linguagem explícita são encaminhadas para revisão. A seleção de origem e a importação são manuais, sem ingestão automática de alertas. A suíte de integração de API não substitui testes E2E automatizados em navegador. O build da API instala dependências conforme `pyproject.toml` sem aplicar `uv.lock`; versões podem mudar em novos builds.

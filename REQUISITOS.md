# SIMCOTER — Requisitos do sistema (versão inicial)

**Status:** requisitos de concepção, ainda não implementados. Todos os cenários e indicadores operacionais são fictícios. P = prioridade: O (obrigatória), E (evolutiva).

## Identidade e plataforma

| ID | P | Requisito |
| --- | --- | --- |
| RF-01 | O | Modo individual em computador adequado |
| RF-02 | O | Multijogador com servidor em LAN/Wi-Fi local |
| RF-03 | O | Interface adaptável a tablets Android e iPads |
| RF-04 | O | Interface para notebooks/desktops comuns |
| RF-05 | O | Jogo operável sem internet pública e sem APIs pagas |
| RF-06 | O | IA local opcional para continuidade do motor |
| RF-07 | O | Mapas, símbolos e recursos offline legalmente utilizáveis |
| RF-08 | O | Processo de planejamento didático baseado em PPCOT |
| RF-09 | O | Simulação logística abstrata e evolução por turnos |
| RF-10 | O | Verificação documental de coordenação e restrições, sem seleção de alvos |
| RF-11 | O | APA individual e comparativa |
| RF-12 | O | Salvamento, backup e retomada de partidas |
| RF-13 | O | Papéis, permissões e isolamento por partido |
| RF-14 | O | Simulação continua se IA estiver indisponível |

## Eventos, informação e doutrina

| ID | P | Requisito |
| --- | --- | --- |
| RF-15 | O | Proposição de problemas educacionais fictícios pela IA |
| RF-16 | O | Proposição de acontecimentos contextuais ao longo dos turnos |
| RF-17 | E | Adaptação da dificuldade por competência |
| RF-18 | O | Três níveis de autonomia configurados pelo instrutor |
| RF-19 | O | Validação programática antes da inserção de eventos |
| RF-20 | O | Separar informações entre partidos |
| RF-21 | O | Auditoria de todas as intervenções de IA |
| RF-22 | O | IA local sem cobrança por token de provedor |
| RF-23 | O | Entradas de várias fontes e seções fictícias do EM |
| RF-24 | O | Origem, horário, confiança e versões de cada registro |
| RF-25 | O | Detectar contradições entre registros, sem apagá-los |
| RF-26 | O | Identificar documentos impactados por informações novas |
| RF-27 | O | Histórico de decisões e dados disponíveis no momento |
| RF-28 | O | Biblioteca doutrinária local, pesquisável e extensível |
| RF-29 | O | IA cita fonte verificável e indica incertezas |
| RF-30 | O | Identificar edição, vigência e proveniência de cada publicação |
| RF-31 | O | Importar apenas documentos com direito de uso |
| RF-32 | O | Biblioteca consultável offline |
| RF-33 | O | Permissões por seção, função e partido |
| RF-34 | O | APA confronta decisão com informação efetivamente disponível |

## Coerência contextual

| ID | P | Requisito |
| --- | --- | --- |
| RF-35 | O | Eventos da IA fundamentados no estado real do cenário |
| RF-36 | O | Evento identifica gatilho/antecedente, causa e dependências |
| RF-37 | O | Verdade mestre do cenário separada dos relatos recebidos |
| RF-38 | O | Conhecimento distinto por partido |
| RF-39 | O | Rejeitar eventos inválidos por regras verificáveis |
| RF-40 | O | Rastrear regra e justificativa da evolução |
| RF-41 | O | Vincular eventos a objetivos pedagógicos |
| RF-42 | O | APA permite reconstruir sequência causal |
| RF-43 | O | Garantir coerência com IA ausente |

## Capacidades agregadas

| ID | P | Requisito |
| --- | --- | --- |
| RF-44 | O | Cadastrar capacidades especializadas fictícias por escalão |
| RF-45 | O | Disponibilidade, responsabilidades, relação de comando e restrições |
| RF-46 | O | Visualizar vínculos na organização simulada |
| RF-47 | O | Representar recursos administrativos fictícios associados |
| RF-48 | E | Assessoria doutrinária especializada com referências |
| RF-49 | O | Biblioteca inclui publicações autorizadas das especialidades |
| RF-50 | O | Eventos levam em conta disponibilidade dessas capacidades |
| RF-51 | O | APA avalia consistência de integração documental |

## Requisitos complementares

| ID | P | Requisito |
| --- | --- | --- |
| RF-52 | O | Geração de calcos de medidas propostas e aprovadas, com validação humana |
| RF-53 | O | Editor de cenários sintéticos para instrutores |
| RF-54 | O | Replay de turnos e reprodução com mesma semente |
| RF-55 | O | Separação entre avaliação do processo e resultado fictício |
| RF-56 | E | Estado-Maior virtual com IA no modo individual |
| RF-57 | O | Mensagens e documentos versionados no jogo |
| RF-58 | O | Exportação de relatórios e APA em formatos abertos |
| RF-59 | O | Proteção de dados pessoais e de materiais autorizados |
| RF-60 | O | Parâmetros de planejamento com fonte/edição e sem reprodução de capacidade sensível |
| RF-61 | O | Indicadores de recursos fictícios sem previsão de eficácia real |
| RF-62 | E | Recursos didáticos de acessibilidade e adaptação de dificuldade |
| RF-63 | O | Motor probabilístico offline de eventos fictícios, condicionado ao estado do cenário |
| RF-64 | O | Sorteio reproduzível por semente, turno e versão de regra |
| RF-65 | O | Ensaios Monte Carlo do próximo turno sem alterar a partida |
| RF-66 | O | Documentar distribuições, limites e incerteza sem extrapolação para combate real |

## Critérios de aceite de primeira versão (MVP)

- Usuário cria cenário sintético e abre partida individual no navegador.
- Registra decisões e relatórios com origem e horário.
- Visualiza mapa offline com unidades fictícias e medida cartográfica proposta/aprovada.
- Avança turnos com regras reproduzíveis e alteração de indicadores logísticos abstratos.
- Gera relatório de APA simples com evidências vinculadas ao log.
- Consegue concluir o mesmo fluxo com IA desativada.
- Testes automatizados verificam isolamento por partido, coerência e repetibilidade.
- Não existe saída para controle real de armamentos ou operações.

## Referenciais a catalogar e validar

PPCOT (EB70-MC-10.211), Logística Militar Terrestre (EB70-MC-10.238), Dados Médios de Planejamento Escolar (DAMEPLAN; edição/verificação pendente) e outros materiais públicos e autorizados. A referência não autoriza automaticamente a redistribuição integral de documentos no repositório.

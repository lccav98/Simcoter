# SIMCOTER

**Sistema Integrado de Modelagem e Condução de Operações Terrestres**

> Planejar · Simular · Avaliar · Aprender

## Visão geral

O SIMCOTER é um projeto de plataforma **educacional** de planejamento e simulação de exercícios fictícios, inspirado em publicações públicas e autorizadas da doutrina do Exército Brasileiro. O projeto prevê treinamento **individual e multijogador**, em tablets e computadores comuns, por navegador, usando rede local e sem dependência da internet pública durante os exercícios.

**Estado atual:** primeiro protótipo de código publicado (backend FastAPI, frontend React, motor didático e testes). **Ainda não foi validado em execução neste ambiente**. Há integração **opcional de código** com Ollama para resumos didáticos, mas ela não foi validada com modelo real; ainda não há multijogador liberado nem integração com map.army.

## Capacidades planejadas

- Fluxo didático de planejamento inspirado no PPCOT e registro versionado de decisões;
- Mapas, símbolos e calcos digitais para organizações fictícias, com geração de medidas após validação humana;
- Simulação por turnos de acontecimentos abstratos, sustentação logística e recursos fictícios;
- Representação pedagógica de embates com regras explícitas e auditáveis, sem previsão de desempenho real;
- Avaliação da consistência documental de medidas de coordenação de fogos e efeitos, sem seleção de alvos ou execução de engajamentos;
- Capacidades agregadas aos escalões fictícios e suas dependências administrativas;
- Alimentação de informações por diferentes seções do Estado-Maior fictício, com origem, hora, confiabilidade, permissões e histórico;
- Direção de exercício por IA local, gerando somente eventos causalmente coerentes e validados;
- Biblioteca doutrinária local ampla, indexada, com referências por edição, item e página quando disponíveis;
- Análise Pós-Ação (APA) dos partidos Azul e Vermelho, independente do resultado do exercício;
- Editor de cenários, atuação de instrutor, modo individual e colaboração multijogador.

## Princípios

1. **Finalidade educativa:** trabalhar com organizações, localidades e parâmetros fictícios. O software não se destina a conduzir operações reais.
2. **Regras auditáveis:** o motor de simulação, não o modelo de linguagem, é a fonte de verdade sobre o estado da partida.
3. **IA supervisionada por validações:** a IA explica, organiza documentos e propõe acontecimentos; regras verificáveis e permissões controlam sua aceitação.
4. **Contexto persistente:** eventos têm antecedentes, causa plausível, ordem temporal e efeitos rastreáveis.
5. **Separação de informações:** cada partido acessa apenas os dados que o cenário lhe permite conhecer.
6. **Local-first:** execução individual em computador adequado ou sessão coletiva com servidor LAN; tablets podem atuar como clientes.
7. **Doutrina verificável:** documentos só são incorporados com origem, licença/autorização, edição e vigência identificadas.

## Stack inicial proposta (sujeita a protótipos e testes)

| Camada | Proposta |
| --- | --- |
| Frontend/PWA | React + TypeScript |
| Cartografia | MapLibre GL JS e simbologia com licença apropriada |
| Backend | Python + FastAPI |
| Motor de eventos | Python, determinístico com semente controlada |
| IA local | Ollama com modelo a ser selecionado e testado |
| Banco individual | SQLite |
| Banco coletivo/geoespacial | PostgreSQL + PostGIS |
| Sincronização | WebSockets |
| Testes | pytest e ferramentas de frontend a definir |

O map.army é **referência e possível via de intercâmbio**. Integração automática, incorporação e uso de símbolos estão condicionados a avaliação técnica e licenças.

## Estrutura do repositório

- `frontend/`: aplicação web para tablets e computadores;
- `backend/`: serviços HTTP e WebSocket;
- `simulation/`: regras e simulação abstrata por turnos;
- `ai/`: integração local com modelos e validação de saídas;
- `maps/`: cartografia, representação de medidas e formatos;
- `logistics/`: simulação fictícia de recursos e serviços;
- `doctrine/`: metadados, indexação e consulta documental autorizada;
- `scenarios/`: cenários sintéticos;
- `after-action/`: análise pós-ação e auditoria;
- `tests/`: testes;
- `docs/`: arquitetura, requisitos e roadmap.

## Próximos passos

Para iniciar o protótipo, ver [docs/COMO_EXECUTAR.md](docs/COMO_EXECUTAR.md). O incremento 0.6 adiciona [Estado-Maior Virtual (EMV) inicial](docs/ESTADO_MAIOR_VIRTUAL.md), com agentes lógicos E1–E4, tarefas auditáveis e revisão humana; Paperclip é adaptador opcional **não instalado**. O incremento 0.5 adiciona [credenciais por partida, papéis e visões restritas](docs/ACESSO_E_PARTIDOS.md), ainda somente para localhost. O incremento 0.4 adiciona [tutor com IA local opcional](docs/TUTOR_IA_LOCAL.md), com saída estruturada, referência a evidências e modo de contingência sem IA. O incremento 0.3 incorpora [Motor Probabilístico de Simulação (MPS)](docs/MOTOR_PROBABILISTICO.md), sem Jev ou APIs pagas, para eventos fictícios e experimentação Monte Carlo. O incremento 0.2 adicionou [consulta de metadados doutrinários e problemas contextuais baseados em regras](docs/BIBLIOTECA_E_CONTEXTO.md); **a geração autônoma de problemas por IA ainda não está implementada**. O MPS não estima resultados reais de combate. Para planejar próximas entregas, ver [ARQUITETURA.md](ARQUITETURA.md), [REQUISITOS.md](REQUISITOS.md) e [docs/ROADMAP.md](docs/ROADMAP.md).

## Segurança e direitos

Não publicar dados operacionais reais, material restrito, credenciais, mapas de acesso controlado ou cópias de manuais sem autorização. Nunca versionar modelos de IA pesados e conjuntos de dados de terceiros sem verificar licença. O repositório começa **privado e sem licença de redistribuição definida**.

## Referências públicas iniciais

- [Exército Brasileiro — portal institucional](https://www.eb.mil.br/)
- [Ministério da Defesa — publicações doutrinárias](https://www.gov.br/defesa/pt-br/assuntos/estado-maior-conjunto-das-forcas-armadas/doutrina-militar)
- [MapLibre GL JS](https://maplibre.org/maplibre-gl-js/docs/)
- [Ollama](https://docs.ollama.com/)
- [PostgreSQL](https://www.postgresql.org/docs/)

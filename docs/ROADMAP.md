# SIMCOTER — Roteiro de desenvolvimento

Nenhum marco abaixo deve ser interpretado como concluído apenas por existir este arquivo.

## M0 — Fundação (atual)
- [x] Criar repositório privado e documentos de concepção
- [x] Registrar requisitos iniciais e arquitetura proposta
- [x] Preparar diretórios e convenções básicas
- [ ] Definir escopo mínimo e critérios mensuráveis de qualidade
- [ ] Verificar direitos de uso de fontes doutrinárias e dados cartográficos

## M1 — Protótipo individual
- [x] Servidor local único para interface compilada e API FastAPI (versão 0.8, teste CI a confirmar)
- [x] Scripts Windows/Linux/macOS para preparar e executar o protótipo
- [x] Teste automatizado de fluxo integrado por HTTP local (execução a confirmar)
- [ ] Implantação autenticada HTTPS para acesso no Safari do iPad e testes reais de toque/WebGL
- [x] Design system inicial responsivo e navegação por áreas; simbologia vetorial original com metadados de tipo e escalão
- [x] Catálogo vetorial inicial de sete naturezas, quatro escalões e legenda/filtros no MapLibre (homologação pendente)
- [ ] Curadoria e verificação de conformidade ao MD33-M-02 / MD33-C-01 e catálogo SIDC
- [x] Código inicial de interface React/TypeScript responsiva (a validar)
- [x] Código inicial de API FastAPI e banco SQLite (a validar)
- [x] Cenário sintético e gestão individual de partidas (código inicial)
- [ ] Mapa offline completo com cartas e calcos fictícios (MapLibre online e símbolos vetoriais de unidades já implementados; sem pacote de tiles offline)
- [x] Motor inicial determinístico com variabilidade probabilística contextual e logística abstrata (MPS 0.3, a validar)
- [ ] Replay e APA básica (APA descritiva inicial implementada; replay pendente)

## M2 — Biblioteca e IA local
- [x] Catálogo inicial de metadados com verificação de fonte/edição ainda pendente
- [ ] Recuperação textual/semântica offline
- [x] Integração de código opcional com Ollama: evidências estruturadas, validação de IDs e fallback (teste com modelo real pendente)
- [ ] Gerador contextual com schema e validador independente (propostas por regras objetivas já implementadas; validação de IA ainda pendente)
- [ ] Testes contra contradições de cenário e citações falsas (validação estrutural de evidências implementada; sem verificação de semântica)
- [x] Motor MPS inicial: probabilidades fictícias, sementes reproduzíveis, ensaios de Monte Carlo, interface e testes (execução a verificar)

## M3 — Estado-Maior multijogador
- [ ] PostgreSQL/PostGIS e WebSockets
- [ ] Autenticação de usuários e controle por partido/função (credenciais experimentais por partida e filtragem de API na v0.5; identidade, revogação e LAN ainda pendentes)
- [ ] Registro de relatórios multi-origem e validação humana
- [ ] Histórico e sincronização de medidas aprovadas
- [ ] Testes de tablets, notebooks e LAN sem internet pública
- [x] Testes de API adicionados para negar acesso entre partidos e restringir ações de instrutor (execução CI a validar)

## M4 — Maturidade didática
- [ ] Editor de exercícios e capacidades agregadas fictícias
- [ ] Instrutor virtual e painel de acompanhamento (EMV E1–E4 inicial com aprovação manual, interface e testes adicionados; execução a verificar)
- [ ] Adaptador Paperclip opcional funcional (somente contrato e stub implementados na v0.6)
- [ ] APA comparativa com rastreabilidade de evidências
- [ ] Avaliação curricular e de acessibilidade
- [ ] Benchmark, auditoria e validação por instrutores

## Critérios transversais
Cenários fictícios; motor independente da IA; nenhuma execução de engajamentos ou escolha de alvos; licenças de mapas/símbolos respeitadas; continuidade offline; dados auditáveis.

# SIMCOTER — Arquitetura técnica proposta

**Status:** documento de concepção, versão 0.1. Nenhum componente é considerado implementado ou homologado.

## 1. Objetivo e fronteiras

Plataforma de **simulação pedagógica** de Estado-Maior e processos de planejamento, com cenários, mapas, organizações, recursos e eventos fictícios. Não é sistema de comando e controle real, nem ferramenta de aquisição de alvos, programação de fogos ou otimização de operações ofensivas.

## 2. Implantação

### Individual (computador)

Frontend PWA no navegador → API e motor locais → SQLite, arquivos de mapa e biblioteca locais → IA via Ollama local opcional. Sem IA, turnos e regras continuam utilizáveis.

### Multijogador (LAN)

Tablets/notebooks/desktops → Wi-Fi ou rede cabeada isolada → servidor local FastAPI/WebSockets → motor Python → PostgreSQL/PostGIS → Ollama compartilhado. Os clientes não precisam executar o modelo de IA.

Um tablet isolado poderá ter consultas e atividades simplificadas offline, mas não há compromisso inicial de executar um modelo grande nem o servidor completo no dispositivo.

## 3. Módulos

| Módulo | Responsabilidade | Limite |
| --- | --- | --- |
| Planejamento PPCOT | Etapas didáticas, decisões, documentos, aprovações | Manuais oficiais como referência, sem alegar certificação |
| Cenários e organizações | Partidos, ordem de batalha sintética, vínculos e capacidades agregadas | Sem dados reais sensíveis |
| Cartografia | Mapas offline, calungas e calcos propostos/aprovados | Licença e formatos verificados |
| Coordenação de medidas | Validação de conflitos documentais, espaciais e temporais | Não determina alvos nem engajamentos |
| Logística | Indicadores fictícios de suprimento, transporte, manutenção, saúde etc. | Não usa fatores reais sensíveis de consumo |
| Eventos e embates | Motor MPS de probabilidades pedagógicas por turnos, sementes reproduzíveis e Monte Carlo | Não prevê letalidade ou desempenho militar real |
| Gestor de Informações (SGSS) | Ingestão multi-origem, metadados, divergências, acessos | Dado recebido não vira fato automaticamente |
| Evolução Contextual (MECC) | Propostas de eventos causais coerentes | Validador determinístico aprova/rejeita |
| Biblioteca (BDI) | Catálogo, versões, trechos, citações, recuperação local | Apenas publicações autorizadas |
| IA didática | Tutor local opcional Ollama com saída JSON, citações aos IDs do estado e fallback; demais agentes ainda planejados | Modelo não altera o estado diretamente |
| APA | Reconstrução de turnos, evidências, comparação entre partidos | Distingue resultado, processo e acaso |
| Instrutor | Controle de sessão, aprovação de eventos, exportação e replay | Log de ações obrigatório |

O motor MPS utiliza regras públicas do próprio software e probabilidades inteiramente fictícias; consultar [docs/MOTOR_PROBABILISTICO.md](docs/MOTOR_PROBABILISTICO.md).

## 4. Fonte de verdade e fluxo de eventos

1. Cliente envia comando autenticado (ex.: cadastrar relatório, propor medida, avançar turno).
2. API verifica papel, cenário, formato e versão esperada do estado.
3. Comando é registrado como evento imutável com origem, horário, turno e autor.
4. Motor de regras aplica transição determinística e atualiza projeções/materializações.
5. Mapa e painéis recebem atualização por WebSocket.
6. IA recebe somente um recorte autorizado e sugere **artefatos** estruturados, nunca grava o estado por conta própria.
7. Validador verifica causalidade, tempo, geografia, recursos, direitos e finalidade pedagógica; quando exigido, o instrutor aprova.
8. APA recupera eventos e referências para explicar cada conclusão.

### Estruturas conceituais

- `Scenario`: ID, versão, objetivos pedagógicos, mapa, catálogo fictício.
- `Party` / `Role` / `Membership`: partido, função e permissões.
- `Unit` / `CapabilityAttachment`: organização sintética e vínculos temporais.
- `Report`: emissor, horário do fato, recebimento, confiança, visibilidade, evidências, validação.
- `Decision`: autor, versão, estado proposta/aprovada, justificativa, dependências.
- `OverlayFeature`: geometria, tipo, vínculo, vigência, status de aprovação.
- `SimulationEvent`: id, turno, antecedente/causa, regra, semente, entradas, saídas.
- `DoctrineSource`: publicação, edição, situação, autorização, checksum, posição da citação.
- `AfterActionFinding`: evidências, regra aplicável, grau de confiança e revisão do instrutor.

## 5. Verdade do cenário vs. conhecimento do jogador

Manter um estado mestre fictício da direção do exercício e **visões autorizadas** por partido e função. Informações incorretas podem existir como relatórios dentro do mundo ficcional, mas não como corrupção do estado mestre. A origem e a distinção devem aparecer na APA.

## 6. IA local e RAG

- Um serviço local (Ollama inicialmente) atende demandas em fila.
- Recuperação semântica + busca lexical dos trechos autorizados.
- Respostas com fonte, edição, item/página quando disponíveis e sinalização de incerteza.
- Saídas de IA em JSON validado por schema; regras adicionais independentes do modelo.
- Cache de respostas por contexto/versão, limite de contexto e síntese incremental.
- Sem chamadas obrigatórias a APIs pagas; IA indisponível não interrompe motor e persistência.

## 7. Coerência dos problemas gerados

Cada proposta de problema requer: objetivo pedagógico, gatilho/antecedente existente, causa plausível, turno, localização fictícia se aplicável, dependências, consequência permitida, partido destinatário e referências de estado. O validador rejeita incompatibilidades cronológicas, espaciais, documentais e de recursos. Variabilidade pseudoaleatória somente **entre possibilidades válidas** e com semente registrada.

## 8. Cartografia

MapLibre com dados offline e licença compatível; mapa vetorial/tiles distribuídos em pacote local. Símbolos e calcos editáveis como entidades vetoriais. Exportação/importação em formatos interoperáveis a validar. map.army não é dependência obrigatória nem se assume API de escrita pública.

## 9. Segurança, privacidade e direitos

Autenticação local, controle por papel e por partido, trilhas de auditoria, backups, integridade dos pacotes, proteção de dados pessoais, segregação do material do instrutor, revisão de licenças e exclusão de informação operacional restrita. Dados de exercícios são sintéticos.

## 10. Qualidade e testes

- Testes de regras determinísticas e replay com mesma semente;
- Contratos JSON para agentes e eventos;
- Testes de isolamento entre partidos, inclusive API e WebSockets;
- Simulação offline sem conexão externa;
- Testes de coerência de relatórios e eventos;
- Performance em tablet 4 GB e notebook 8 GB como **metas a validar**, não garantias.

## 11. Decisões pendentes

Modelo de IA local e seus termos; simbologia militar licenciada; conjunto de mapas offline; estrutura jurídica das publicações doutrinárias; limites de hardware e usuários simultâneos; avaliação acadêmica dos modelos; versionamento de cenários e formatos de integração.

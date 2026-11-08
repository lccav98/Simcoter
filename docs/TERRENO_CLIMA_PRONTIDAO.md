# SIMCOTER — Terreno, clima e prontidão (protótipo didático)

## Objetivo e limite

Este módulo implementa a **consistência de regras de um tabuleiro fictício**, e não modela capacidade militar real, terreno operacional, mobilidade, desempenho de unidades ou resultados de combate. Os valores e limites foram escolhidos apenas para demonstrar o software.

**Não há integração com previsões meteorológicas reais, modelos de trafegabilidade, elevação, declividade, hidrologia, itinerários ou mobilidade de blindados.** A carta MapLibre é uma visualização geográfica, mas as áreas classificadas são inventadas e não descrevem o terreno geográfico exibido.

## Disponibilidade da unidade

O indicador de prontidão didática é exibido continuamente no calunga, com percentual, barra e estado textual. A transição de turno reduz a pontuação por uma regra arbitrária de demonstração.

- Acima de 50: `disponivel`.
- De 26 a 50: `atencao`.
- Até 25: `indisponivel` — a unidade não pode receber novas ações de deslocamento fictício.

A indisponibilidade é aplicada **no backend**, não somente nas cores do calunga. O instrutor pode ajustar a pontuação e produzir uma trilha de auditoria. Os limites não são dados doutrinários ou métricas reais de poder de combate.

## Áreas do tabuleiro fictício

O cenário usa uma malha abstrata de 0 a 100 em dois eixos, com duas áreas retangulares inventadas:

| Classificação | Regra pedagógica |
| --- | --- |
| Livre | O deslocamento fictício pode prosseguir se a unidade estiver disponível e o clima permitir |
| Restritiva | Exige validação/autorização explícita do instrutor |
| Impeditiva | Bloqueia o deslocamento fictício, mesmo quando houver autorização |

A verificação atual considera **somente o ponto de destino**. Não há traçado de caminho, análise do percurso nem algoritmos de roteamento. Uma classificação exibida sobre os tiles OSM não caracteriza a superfície real correspondente.

## Clima

| Condição fictícia | Regra |
| --- | --- |
| `normal` | Não acrescenta restrição |
| `adverse` | Exige revisão/autorização explícita |
| `severe` | Suspende deslocamentos fictícios |

O instrutor pode selecionar a condição na aba Planejamento. O servidor registra a mudança e valida cada tentativa de deslocamento.

## Integração com Estado-Maior Virtual

Os agentes lógicos E3 e E4 recebem somente a condição climática do exercício e o **número agregado** de unidades indisponíveis. Não recebem análises táticas, rotas, alvos ou listas de posições por essa integração. Seus textos são revisões documentais didáticas e não alteram o cenário.

## API local, protegida pelo token do instrutor

- `GET /api/sessions/{id}/environment`
- `POST /api/sessions/{id}/environment/weather` com `{"weather":"adverse"}`
- `POST /api/sessions/{id}/units/{unit_id}/movement/check` com `{"x":65,"y":65,"authorized":false}`
- `POST /api/sessions/{id}/units/{unit_id}/movement` com `{"x":65,"y":65,"authorized":true}`
- `POST /api/sessions/{id}/units/{unit_id}/readiness` com `{"change":-20}`

Em todas as rotas de movimento, alterações só são aceitas após revalidação no servidor. Mudanças de clima, de indicador e deslocamentos são registrados para a APA.

## Testes e situação

Os testes automatizados `tests/test_environment.py` e `tests/test_readiness.py` cobrem limites e autorização por partido. Eles ainda precisam ser confirmados em execução integrada no computador. O modo WebKit de testes ajuda a detectar regressões, mas não substitui a validação em um iPad físico.

## Referências técnicas verificáveis

- MapLibre GL JS: https://maplibre.org/maplibre-gl-js/docs/
- FastAPI: https://fastapi.tiangolo.com/
- Testes de navegador Playwright: https://playwright.dev/docs/intro

**Observação:** essas fontes documentam as ferramentas utilizadas, não validam os parâmetros fictícios do jogo.

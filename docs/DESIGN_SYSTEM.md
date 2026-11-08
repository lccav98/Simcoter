# SIMCOTER — Sistema de design Command Desk (protótipo 0.8)

## Objetivo

A interface deve parecer uma ferramenta profissional de análise e simulação educativa, mantendo a **carta geográfica como elemento principal**, clareza na leitura do estado da partida e operação adequada por toque no iPad. O design é original; não utiliza logotipos institucionais, imagens licenciadas de terceiros ou fontes remotas.

## Hierarquia de informação

1. **Cabeçalho institucional do aplicativo:** nome, estado de desenvolvimento e ação de entrar/sair.
2. **Navegação de quatro áreas:** Situação, Planejamento, Estado-Maior e Avaliação/Biblioteca. As áreas indisponíveis ao papel não aparecem.
3. **Carta MapLibre:** elemento permanente, com símbolos vetoriais fictícios, escala, zoom e popups.
4. **Painéis contextuais:** organizados por área, com indicador de turno, ações e estados de aprovação.
5. **Evidências e auditoria:** conteúdo com datas, turnos e referências, sempre separado das conclusões de IA.

## Tokens de interface

| Elemento | Token | Papel |
| --- | --- | --- |
| Fundo | `#09151b` | Base de alto contraste |
| Painéis | `#11242b` / `#18323a` | Hierarquia das superfícies |
| Texto | `#e9f0f1` | Informação principal |
| Texto secundário | `#a9bac0` | Metadados |
| Destaque | `#d5a95b` | Seleção e ação principal |
| Confirmação/tarefas | `#75c2b4` | Acento funcional |
| Erros | `#d98180` | Feedback de problema |
| Borda | `#2b454e` | Separação discreta |

O sistema usa fontes de interface do próprio dispositivo; não envia solicitações de fontes para CDNs.

## Interação e acessibilidade

- Controles principais com altura mínima de 44 px e foco visível de alto contraste.
- A interface reordena seus painéis para telas menores que 950 px.
- A navegação por área evita rolagem desnecessária de painéis secundários no iPad.
- Estados de erro, falha de WebGL e indisponibilidade do Ollama devem ser exibidos por texto, não apenas por cor.
- Preferências de redução de movimento são respeitadas.
- As cores Azul/Vermelho não são a única forma de diferenciar unidades: símbolos carregam nome, natureza, escalão e descrição acessível.
- A conformidade WCAG completa, gestos no Safari real e testes de leitores de tela ainda precisam ser verificados.

## Cartografia e simbologia

- O mapa geográfico é renderizado pelo MapLibre GL JS.
- Os elementos fictícios são dados separados da visualização; o SVG é criado localmente.
- A composição de símbolos é **didática e simplificada**; não certificada no MD33-M-02 / MD33-C-01.
- O mapa-base de demonstração é OpenStreetMap online. O futuro modo offline depende de fonte de dados autorizada.

## Testes de interface

`frontend/e2e/integrated.spec.ts` contém testes em Chromium e WebKit em viewport com dimensões aproximadas de iPad, com verificação de presença de mapa e controles, fluxo de turno, Estado-Maior, APA e separação de papéis.

**Limitação:** a execução bem-sucedida da suíte ainda não foi verificada, e o ambiente WebKit do Playwright não equivale a um iPad físico.

## Evolução desejada

Revisão de contraste, teclado, leitor de tela, performance de WebGL, toolbar de camadas, filtros de simbologia, legenda interativa, editor de medidas, informações de origem cartográfica e arquitetura de componentes React reutilizáveis.

Referências técnicas:
- [MapLibre GL JS](https://maplibre.org/maplibre-gl-js/docs/)
- [W3C WCAG 2.2](https://www.w3.org/TR/WCAG22/)
- [Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)

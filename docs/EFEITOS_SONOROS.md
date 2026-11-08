# SIMCOTER — Efeitos sonoros didáticos

**Estado:** código acrescentado ao frontend React; ainda é necessária validação de compilação e execução no Safari/iPad real.

## Objetivo

Complementar a experiência audiovisual dos exercícios fictícios, sem alterar
o motor de simulação ou representar efeitos físicos, danos, armamentos, explosões
ou baixas reais. Esta camada de áudio não modela combate nem influencia decisões
ou probabilidades.

## Implementação

O código `frontend/src/gameAudio.ts` utiliza **Web Audio API**, sem arquivos
externos, serviços pagos, download de efeitos ou gravações. Os sons são curtos,
sintéticos, com envelope de volume, limite máximo conservador e controle manual.

Três tipos de sinal:

| Sinal | Gatilho | Significado |
| --- | --- | --- |
| `routine` | Turno completado sem incidente | Confirmação discreta |
| `incident` | Turno com `scenario_event` | Acontecimento administrativo/logístico fictício |
| `engagement_preview` | Botão de prévia, exclusivamente por iniciativa do usuário | Demonstração de ambiência para futuro embate fictício; **não registra embate** |

**Importante:** o modelo probabilístico atual não gera embates táticos. A prévia
sonora não significa que ocorreu combate, nem cria um evento no estado da partida.
Caso um futuro motor inclua `engagement`, os sinais deverão ser associados
somente a eventos registrados, sob contrato versionado e validador.

## Compatibilidade e privacidade

- Áudio **silenciado por padrão**, sem autoplay.
- O usuário deve clicar em **Ativar áudio**. No Safari do iPad, a criação e a
  retomada do `AudioContext` ocorrem dentro da interação explícita.
- Volume ajustável de 0 a 45% do ganho do aplicativo; a configuração do
  aparelho permanece sob controle do usuário.
- A prévia é acionada somente ao tocar seu próprio botão.
- Nenhum arquivo de som, pacote externo, rastreamento de áudio ou chamada
  de rede é necessário.
- A falta de suporte à Web Audio API não impede a partida.
- A camada de som permanece desacoplada do backend, não grava informações
  sobre ações do jogador e não modifica eventos.

## Testes pendentes

O teste Playwright em `frontend/e2e/integrated.spec.ts` verifica estado
inicial silenciado, alternância, slider, prévia sem avanço de turno e botão de
silêncio. Verificar ainda em um iPad real com Safari, volume baixo, e nos
contextos de uso com fones e alto-falantes.

## Referências

- [MDN — Web Audio API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API)
- [MDN — AudioContext.resume](https://developer.mozilla.org/en-US/docs/Web/API/AudioContext/resume)
- [WebKit — Web Audio](https://webkit.org/blog/6784/new-video-policies-for-ios/)

O áudio é gerado por código original do SIMCOTER. Nenhum efeito comercial
ou gravação de fonte externa foi incorporado.

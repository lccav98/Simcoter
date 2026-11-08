# Estado-Maior Virtual — EMV (incremento 0.6)

## Decisão arquitetural

O SIMCOTER terá um **orquestrador próprio** como implementação de referência. A plataforma Paperclip será uma alternativa **opcional**, somente depois de testes de compatibilidade, licença, desempenho, operação offline e isolamento de dados.

**Situação real do código:** existem quatro agentes lógicos baseados em regras (E1, E2, E3 e E4), fila persistida como tarefas da partida, síntese de pendências, revisão humana e API protegida por token de instrutor. Não existem instâncias Paperclip em execução nem quatro modelos de IA atuando autonomamente. O adaptador `PaperclipAdapter` é apenas um contrato que rejeita chamadas, em vez de simular integração concluída.

## Funções implementadas

| Agente | Escopo dos dados recebidos | Saída didática |
| --- | --- | --- |
| E1 — Pessoal | Número de organizações fictícias e turno | Conferência de quadros administrativos |
| E2 — Informações | Número de registros e lista de fontes, sem texto dos relatórios | Revisão de fontes e cronologia |
| E3 — Planejamento | Identificadores e status de medidas propostas | Verificação de pendências documentais |
| E4 — Logística | Indicadores fictícios de recursos e turno | Revisão de estimativas de recursos |

O chefe do Estado-Maior lógico apenas consolida as tarefas. Os agentes não recebem acesso irrestrito à biblioteca, não produzem ordens de combate e não modificam recursos nem evoluem turnos.

## Fluxo

1. O jogador/instrutor seleciona uma das quatro seções no painel.
2. A API verifica o token da partida e a autorização de instrutor.
3. O agente prepara uma proposta com evidências selecionadas e hash do contexto recebido.
4. A proposta entra na lista da partida com status `proposed`, identificador próprio e trilha de eventos.
5. O jogador seleciona **aprovar** ou **rejeitar**; ambas são decisões administrativas registradas. A aprovação **não executa** a proposta no jogo.
6. O coordenador atualiza o quadro de tarefas pendentes, aprovadas e rejeitadas.

A persistência permanece em SQLite no protótipo local. A proposta não depende de conexão com o Paperclip nem de LLM.

## API (somente instrutor)

- `GET /api/sessions/{id}/staff`: catálogo e quadro de tarefas.
- `POST /api/sessions/{id}/staff/tasks` com `{"agent": "E4"}`: criar tarefa.
- `POST /api/sessions/{id}/staff/tasks/{task_id}/review` com `{"action": "approved"}` ou `{"action": "rejected"}`.

Todas as rotas requerem `Authorization: Bearer <token-do-instrutor>`. O código continua **restrito ao localhost** e não está homologado como autenticação de usuários reais.

## Integração futura com Paperclip

O adaptador deverá implementar o contrato `StaffAdapter.propose(...)`, sem acesso direto a tabelas de partidas, alteração do estado ou extração de relatórios de outros partidos. A implementação precisará:

- usar um único modelo local compartilhado por uma fila;
- manter instruções e contexto separados por papel;
- receber apenas dados preparados pelo servidor segundo listas positivas;
- produzir saídas estruturadas verificadas antes da criação das tarefas;
- impor limites de tempo, quantidade, memória e chamadas;
- persistir as evidências e exigir aprovação humana;
- manter o orquestrador integrado como alternativa offline.

Não conectar o Paperclip nem instalar plugins automaticamente enquanto faltarem essas garantias.

## Critérios de aceite seguintes

Executar os testes de segurança e integração; validar a interface em navegador; permitir múltiplos objetivos pedagógicos; oferecer versão por partido com acesso delimitado; ligar o tutor Ollama às tarefas sem escrita de estado; testar o adaptador Paperclip separadamente.

## Referências técnicas

- [Paperclip — repositório e licença declarada pelo projeto](https://github.com/paperclipai/paperclip)
- [Ollama — documentação](https://docs.ollama.com/)
- [FastAPI — segurança](https://fastapi.tiangolo.com/tutorial/security/)
- [OWASP — authorization](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)

As referências técnicas ajudam a selecionar componentes. O EMV e suas regras são desenho original do SIMCOTER, não transcrição de doutrina institucional.

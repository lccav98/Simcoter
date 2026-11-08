# SIMCOTER — Acesso por partido (protótipo 0.5)

**Escopo:** controle experimental de credenciais e visões em ambiente local. Não é um sistema de contas de usuário nem foi homologado para uso em rede.

## Criação de partida

`POST /api/sessions` cria uma partida e devolve **uma única vez** os tokens de `instrutor`, `azul` e `vermelha`, em `credentials`. O instrutor deve guardar e compartilhar cada token somente com o participante correspondente. O banco SQLite armazena hashes SHA-256, não os tokens originais.

O frontend mostra os três tokens na criação e permite copiá-los. Para acessar uma partida, informe o ID e o token correspondente. Os tokens da sessão ativa ficam em `sessionStorage` no navegador, removidos quando o participante sai da sessão ou quando a aba é encerrada.

**Atenção:** uma pessoa com acesso ao token poderá assumir aquele papel. Tokens compartilhados, capturados, perdidos ou reutilizados não possuem atualmente mecanismo de revogação/rotação.

## Modelo de permissões

| Ação | Instrutor | Azul | Vermelha |
|---|---|---|---|
| Ler o estado completo | Sim | Não | Não |
| Ler os próprios relatórios e unidades | Sim | Sim | Sim |
| Criar relatórios | Sim, com destino escolhido | Somente Azul | Somente Vermelha |
| Avançar turnos | Sim | Não | Não |
| Aprovar medida | Sim | Não | Não |
| Consultar APA completa | Sim | Não | Não |
| Consultar prévia probabilística | Sim | Não | Não |
| Consultar análise contextual global | Sim | Não | Não |
| Consultar tutor IA global | Sim | Não | Não |
| Consultar catálogo de metadados doutrinários | Sim | Sim | Sim |

Para os partidos, `GET /api/sessions/{id}` devolve somente uma lista positiva de campos: identificador, título, turno, recursos vazios, suas próprias unidades e seus próprios relatórios. O histórico global e os indicadores do cenário não são incluídos.

As permissões são aplicadas no **servidor**, não apenas ocultando botões. A API exige `Authorization: Bearer <token>` em todas as rotas específicas de partida.

## Limitações

- A criação de partidas continua aberta a quem conseguir acessar a API local.
- O protótipo não oferece autenticação por pessoa, contas, 2FA, criptografia em trânsito, controle de tempo de expiração, revogação ou auditoria completa.
- O estado mestre do cenário permanece em SQLite local, sem criptografia de armazenamento.
- Tokens são exibidos ao criador em uma única resposta de API: não enviar capturas de tela ou logs contendo credenciais.
- O `sessionStorage` é acessível a scripts da mesma origem. Não executar a interface com código de origem não confiável.
- Partidas anteriores à versão 0.5, sem tokens emitidos, precisam ser recriadas; não há migração automática.
- A proteção restringe o conteúdo de uma partida existente; ela **não autoriza** disponibilizar a versão atual a participantes em LAN ou internet.
- O modo multijogador seguro exigirá autenticação real, segregação dos documentos e informações por papel, autorização sobre cada entidade, revogação, HTTPS/rede de confiança, logs e testes de penetração.

## Testes automatizados

`tests/test_api.py` cobre credenciais ausentes/incorretas, isolamento de relatórios e unidades, restrição de avanços de turno e de análises globais. Esses testes precisam ser executados no pipeline para confirmar a versão.

Fontes técnicas: [FastAPI — segurança](https://fastapi.tiangolo.com/tutorial/security/), [OWASP — Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html).

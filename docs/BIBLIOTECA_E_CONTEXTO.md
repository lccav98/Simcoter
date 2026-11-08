# Biblioteca e geração contextual — incremento 0.2

**Situação:** código de protótipo, não verificado em produção. Não foi feita ingestão dos manuais oficiais.

## Biblioteca

O endpoint `GET /api/doctrine?q=logistica` consulta um pequeno catálogo local
de metadados, sem acesso à internet. Os registros têm estado de verificação
**pendente** e URLs apenas institucionais. Não contêm o texto dos manuais e não
permitem atribuir citação de página ou item específico.

A futura BDI precisa:
- ingerir somente documentos cujo uso e armazenamento estejam autorizados;
- conservar edição, vigência, origem, checksum e permissões;
- indexar trechos e recuperar referências verificáveis;
- distinguir documento encontrado de doutrina em vigor;
- impedir citações inventadas pela IA local.

## Evolução contextual

O endpoint `GET /api/sessions/{id}/context` analisa o estado existente e
apresenta problemas pedagógicos com um gatilho objetivo e referências a dados
do cenário. Exemplos: indicadores fictícios abaixo do patamar de revisão,
medidas gráficas ainda não aprovadas e checagem de separação de relatórios
entre partidos.

Os problemas **não são gerados por IA generativa nesta etapa**: o módulo usa
regras reproduzíveis. Para integração futura com Ollama, o modelo poderá
redigir diferentes explicações a partir desse contexto, mas um validador
independente deverá impedir propostas sem antecedente, causa ou autorização.

## Limitações de segurança

A versão atual ainda não implementa autenticação nem controle efetivo por
partido. Os relatórios de ambas as equipes podem ser visualizados no modo
local. **Não utilizar o protótipo atual como exercício multijogador real**,
não inserir informação sensível e não expor a API a redes externas.

O desenvolvimento de separação de conhecimento, permissões e validação
humana precede a ativação de multiplayer e IA autônoma.

# SIMCOTER — Simbologia das unidades fictícias

**Versão de referência:** protótipo 0.8. O catálogo ainda não está certificado como representação integral da simbologia oficial.

## Referências primárias

- Portal da Diretoria de Serviço Geográfico/Exército Brasileiro: https://simbologia.eb.mil.br/ (não acessível na consulta realizada durante esta implementação).
- Ministério da Defesa — **MD33-M-02**, Manual de Abreviaturas, Siglas, Símbolos e Convenções Cartográficas das Forças Armadas, 4ª edição (2021): https://www.gov.br/defesa/pt-br/arquivos/File/legislacao/emcfa/publicacoes/manual-md33-m-02-manual-de-abreviaturas-siglas-simbolos-e-convencoes-cartograficas.pdf
- Ministério da Defesa — **MD33-C-01**, Catálogo de Símbolos e Convenções Cartográficas das Forças Armadas, 1ª edição (2021), aprovado pela Portaria GM-MD nº 103/2022: https://www.gov.br/defesa/pt-br/assuntos/estado-maior-conjunto-das-forcas-armadas/doutrina-militar/publicacoes-1/publicacoes/MD33C01CatlogodeSmboloseConvenesFA1Ed.2021.pdf

As referências públicas estabelecem a estrutura geral de composição por moldura, ícone principal, amplificadores e escalão, inclusive para elementos terrestres. O SIMCOTER implementa, inicialmente, uma **interpretação gráfica original simplificada**, não uma reprodução do catálogo completo. A publicação oficial na internet não foi tratada como licença de redistribuição de suas imagens.

## Componentes já implementados

O frontend contém `frontend/src/militarySymbols.ts`, um gerador de SVG em memória para marcadores do MapLibre. Os metadados `kind` e `echelon` são guardados por unidade fictícia em `backend/app/game.py`.

| Metadado | Valores iniciais | Tratamento |
| --- | --- | --- |
| `party` | `azul`, `vermelha` | Moldura azul ou vermelha |
| `kind` | `infantry`, `logistics`, `command` | Ícone vetorial didático distinto |
| `echelon` | `platoon`, `company`, `battalion`, `brigade` | Indicador de escalão acima da moldura |
| `name` | Texto livre da organização fictícia | Rótulo acessível e janela informativa |
| `x`, `y` | Coordenadas sintéticas do exemplo | Transformadas em localização de demonstração no MapLibre |

A amostra do cenário ainda utiliza três unidades fictícias com tipos e escalões diferentes. O catálogo de componentes foi ampliado para **sete naturezas gráficas didáticas**: infantaria, logística, comando, engenharia, comunicações, saúde e transporte. Todos são desenhados em SVG localmente, sem reutilizar imagens de terceiros. Os quatro escalões fictícios são pelotão, companhia, batalhão e brigada.

## Regras de projeto

1. **Moldura e preenchimento** distinguem visualmente os partidos.
2. **Natureza** e **escalão** são campos separados; a designação textual não deve substituir a estrutura dos metadados.
3. **Tamanho em tela** permanece legível nos gestos de pinça do iPad, sem modificar o valor fictício do escalão.
4. **Separação de informações:** o servidor entrega apenas as unidades autorizadas para cada partido; o mapa não deve reconstruir unidades ocultas.
5. **Interoperabilidade futura:** adicionar catálogo versionado de códigos de símbolos e verificador de compatibilidade após curadoria do manual.
6. **Segurança e privacidade:** não representar ordens de batalha ou posições reais. Organizações e localizações do protótipo são fictícias.

## Limitações conhecidas

Os ícones de logística e comando são **desenhos genéricos originais de interface**; não há afirmação de que coincidam com pictogramas oficiais. A simbologia militar oficial possui categorias, modificadores, amplificadores, extensões e regras não implementadas. Não existe exportação SIDC validada, integração direta com o portal de simbologia ou homologação doutrinária.

**Legenda interativa implementada:** o mapa permite ocultar ou mostrar unidades por partido e natureza presente no cenário, além das medidas gráficas aprovadas. O catálogo apresenta identificação acessível, e o backend continua sendo responsável por filtrar o que cada partido pode visualizar. Não há catálogo SIDC oficial ou homologação.

**Próximas etapas:** conferir visualmente as regras e exemplos oficiais do MD33-C-01, criar catálogo de códigos tipados após curadoria, verificar precisão dos pictogramas e realizar testes completos de navegador e iPad real.

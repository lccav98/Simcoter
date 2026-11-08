# Base sintética offline

A base padrão é uma grade vetorial original gerada em frontend/src/offlineMap.ts, incorporada ao build. Não baixa tiles, fontes ou sprites. Não representa cartas reais nem relevo real; as coordenadas servem apenas para posicionamento gráfico do cenário fictício. As restrições didáticas continuam definidas pelo motor do exercício.

Origem: código original do projeto, sem conjunto cartográfico de terceiros. Mantém o regime privado do repositório; esta alteração não concede licença pública de redistribuição. Não foi baixado nem redistribuído conteúdo do OpenStreetMap.

Após a instalação de dependências e compilação, o mapa funciona com a API local sem internet. Isso não torna a aplicação uma PWA disponível sem o servidor local.

Cartas reais offline continuam pendentes. Antes de incorporá-las, registrar fornecedor, área, versão, licença, atribuição, permissão de armazenamento offline e redistribuição. Não usar cartas restritas ou dados operacionais reais.

Validação de 2026-11-08: build TypeScript/Vite aprovado; 18 testes Playwright aprovados em Chromium e WebKit. O novo teste bloqueia solicitações HTTP externas, abre uma partida, verifica canvas e três marcadores, recarrega e confirma ausência de solicitações externas. 51 testes Python aprovados.

Playwright usa 127.0.0.1:18000 e banco temporário próprio, separado das partidas do usuário. Bancos temporários ficam na pasta temporária do Windows. Dados existentes não foram removidos.

Ollama: serviço local indisponível em 127.0.0.1:11434 nesta validação. Não foi instalado nem baixado modelo. Integração agora desabilita proxies do sistema explicitamente e mantém bloqueio de redirecionamentos. Validação com modelo real permanece pendente.

## Pacotes vetoriais locais
O instrutor pode importar um arquivo JSON de até 1 MB pela opção "Importar pacote cartográfico fictício". Esta versão aceita apenas LineString, até 500 feições e 10.000 pontos, com longitude entre -180 e 180 e latitude entre -85 e 85. Propriedades arbitrárias são descartadas. Não são aceitos tiles, estilos executáveis ou referências remotas.

O pacote fica somente na memória da visualização e pode ser removido pelo botão. Recarregar, sair ou trocar de partida descarta o pacote. Ele não é enviado ao servidor, salvo no banco ou compartilhado com outros partidos.

Formato mínimo:
~~~json
{
  "version": 1,
  "fictional": true,
  "offlineAllowed": true,
  "title": "Traçado fictício",
  "source": "Desenho original do autor",
  "license": "Autorização de uso privado pelo autor",
  "attribution": "Autor do desenho",
  "data": {
    "type": "FeatureCollection",
    "features": [{
      "type": "Feature",
      "properties": {},
      "geometry": {
        "type": "LineString",
        "coordinates": [[-48.0, -15.8], [-47.9, -15.7]]
      }
    }]
  }
}
~~~
Os campos são declarações do responsável pelo arquivo, não certificação automática de direitos. Verifique a autorização antes de importar. O exemplo é apenas um segmento fictício, não um dado cartográfico real. A importação de cartas reais licenciadas continua fora desta versão.

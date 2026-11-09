# SIMCOTER — guia do ciclo integrado

Atualizado em 09/11/2026. Este guia descreve o protótipo funcional atual. Ele não representa um simulador militar validado. Use exclusivamente informações fictícias e não classificadas. Execução local e repositório privado não homologam o computador para documentos sigilosos.

## 1. Abrir no Windows

Na pasta do projeto, dê dois cliques em `INICIAR_SIMCOTER.cmd`. Mantenha o terminal aberto. A primeira instalação precisa obter dependências; aguarde a compilação. Abra http://127.0.0.1:8000. Não publique o serviço nem altere o endereço de escuta para interfaces externas.

Alternativa pelo PowerShell, nesta instalação:

```powershell
Set-Location 'C:\Users\d7opa\Documents\Codex\2026-11-08\referenced-chatgpt-conversation-this-is-an\work\Simcoter'
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_local.ps1
```

Com Ollama já instalado e o modelo disponível:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_local.ps1 -AIModel 'qwen3.5:4b'
```

Depois de instalar e compilar, a inicialização direta evita repetir a instalação:

```powershell
.\.venv\Scripts\python.exe scripts/start_local.py
```

Essa inicialização direta usa as variáveis de configuração presentes no terminal; não ativa a IA automaticamente. Para desligar, use Ctrl+C no terminal do servidor. Fechar apenas o navegador não encerra o servidor. O endereço `/api/health` permite verificar se está respondendo.

## 2. Criar ou retomar um exercício

Clique em **Criar partida individual** ou **Criar exercício**. A partida começa no turno 0, com cenário e indicadores fictícios. Guarde o identificador e as credenciais exibidas uma única vez. O token de instrutor permite administrar a partida; os tokens Azul e Vermelho dão visões limitadas ao respectivo partido. Clique em **Já salvei as credenciais** para ocultá-las.

Para retomar, informe **Identificador da partida** e **Token do participante**, depois **Entrar**. A sessão do navegador guarda o acesso durante seu uso. **Sair da sessão** remove esse acesso do navegador, mas não apaga o exercício do banco local `data/simcoter.sqlite3`. Preserve esse arquivo; faça cópias de segurança com o servidor parado. Não publique banco ou tokens no GitHub.

Não há cadastro individual completo, recuperação de senha, revogação de tokens ou uso em rede homologado. Uma sessão antiga que já avançou sem preparação aprovada continua consultável, mas não atende ao novo ciclo: crie outro exercício para utilizar o fluxo completo, preservando a antiga.

## 3. Planejamento inicial — ainda no turno 0

Abra **Planejamento**. Preencha os campos da ordem didática: situação, missão, execução, apoio/logística, comando/comunicações e restrições. **Preencher campos vazios com exemplo fictício** preenche lacunas para experimentar; não substitui os textos que você já digitou e não aprova automaticamente.

Na composição de meios, confira nome, partido, natureza, escalão, vínculo hierárquico, posição X/Y e prontidão das unidades. Os tipos representam elementos de manobra, apoio e logística como dados cadastrais. Eles ainda não têm modelos físicos diferentes de combate ou consumo. As coordenadas 0–100 são posições abstratas de tabuleiro, sem equivalência operacional.

Registre os quatro componentes PITCIC: terreno, condições meteorológicas, inimigo e condicionantes civis. Para cada registro, confira descrição, fonte, validade e grau de certeza. Hipóteses e lacunas podem ser declaradas: aprovação não transforma hipótese em fato. Esses textos organizam a revisão humana; não são automaticamente convertidos em rotas, ameaças ou efeitos de combate.

**Salvar rascunho** persiste o formulário sem substituir a composição ativa do cenário. **Aprovar e aplicar ao cenário fictício** valida os campos e aplica as unidades, registrando a revisão. Conflitos com uma revisão mais nova são recusados para evitar sobrescrita. Depois de iniciado o turno 1, a preparação inicial fica bloqueada.

### PDF de exemplo

Use o PDF sintético fornecido pelo sistema. A prévia extrai texto, identifica páginas e permite selecionar um trecho e acrescentá-lo a um campo do planejamento. Confira o texto e sua referência antes de salvar. O acréscimo é manual e não representa interpretação automática da ordem nem posicionamento automático de unidades.

Limites atuais: 2 MB, 30 páginas e 60 mil caracteres extraídos; documentos criptografados são recusados, e digitalizações sem camada textual não possuem OCR. O PDF não é arquivado pela função de prévia nem enviado ao tutor. Trechos acrescentados ao planejamento passam a ser persistidos quando você salva. Não use documentos classificados, mesmo de exercício.

## 4. Terreno, clima e fila de deslocamentos

Ainda em **Planejamento**, localize **Terreno e clima do exercício**. Selecione clima estável, adverso ou suspensão climática. Essa escolha é manual; não há consulta meteorológica nem interpretação automática do texto PITCIC.

Selecione uma unidade, informe X e Y e clique em **Verificar disponibilidade**. O servidor verifica prontidão, destino e clima. Área impeditiva e suspensão climática bloqueiam; área restritiva ou clima adverso exigem a autorização humana indicada no formulário. Uma unidade com prontidão de 25% ou menos não pode realizar novo deslocamento.

Se permitido, clique em **Enfileirar deslocamento fictício**. A unidade permanece na posição atual até o turno ser executado. Uma nova ordem para a mesma unidade substitui seu destino anterior na fila. É possível dar ordens a várias unidades. A validação examina somente o destino: não calcula caminho, distância percorrida, velocidade, obstáculos intermediários ou duração.

As áreas abstratas de restrição não são inferidas do mapa geográfico. A API administrativa antiga de deslocamento imediato permanece disponível para compatibilidade; a interface utiliza a fila revisada. Alterações administrativas posteriores invalidam a revisão do turno.

## 5. Situação — revisar e executar um turno

Volte a **Situação**. O mapa apresenta os símbolos, posições e prontidão. Zoom, arraste e gesto de pinça permitem navegar. A base sintética funciona sem buscar mapas externos; a opção geográfica pode depender de internet. Pacotes locais de linhas GeoJSON exigem os metadados de licença definidos pelo importador. Importar linhas não cria regras de terreno.

No painel **Ciclo do turno**, confira o número de ordens e os destinos. **Limpar ordens do turno** remove toda a fila sem avançar o relógio. Clique em **Revisar próximo turno**. A prévia mostra impedimentos, validação das ordens, indicadores antes/depois e o evento previsto pelas regras determinísticas.

**Avançar turno** só fica disponível quando a revisão não tem impedimentos. A preparação precisa estar aprovada. Se houver alteração de clima, prontidão, ordem, relatório ou outro dado após a revisão, a execução é recusada: solicite nova revisão. Um segundo envio da mesma execução também é recusado. Isso evita executar uma situação diferente daquela conferida.

Ao executar, o servidor aplica conjuntamente os deslocamentos, a atualização dos indicadores, a redução de prontidão, os registros de eventos e o incremento do turno; depois limpa a fila. Sem ordens, as posições são mantidas. Um erro de validação não aplica parcialmente o turno.

Regras efetivas deste protótipo:

- Limite de 20 turnos, sem conversão em minutos ou horas reais.
- Indicadores abstratos de recursos sofrem redução básica de 2 pontos por turno, limitada a zero.
- Eventos elegíveis podem acrescentar redução fictícia de 1, 2 ou 3 pontos, com pesos de 25%, 50% e 25%. A elegibilidade depende dos indicadores; não significa combate entre unidades.
- A semente da partida e o número do turno tornam o resultado reprodutível, permitindo uma prévia exata do próximo resultado.
- A prontidão diminui 3 pontos por turno: acima de 50, disponível; de 26 a 50, atenção; até 25, indisponível.
- Os comandos de prontidão −20/+20 são ajustes administrativos imediatos do instrutor, não recuperação ou perdas calculadas por combate.

Depois da execução, confira o turno, as posições, os indicadores e os eventos. Os painéis de análise anteriores são limpos para evitar apresentar resultados desatualizados. O som é opcional, inicialmente desativado, com volume e prévia. A prévia sonora não cria embates.

## 6. Relatórios, medidas e Estado-Maior

Na situação, registre relatórios fictícios pelos controles disponíveis. O servidor associa partido e turno ao registro. Participantes não recebem o estado global do instrutor. As medidas gráficas propostas podem ser aprovadas pelo instrutor; aprovação registra decisão, sem produzir automaticamente efeitos de combate.

Em **Planejamento**, **Analisar situação** apresenta problemas pedagógicos derivados de regras e evidências do cenário. Não é análise militar generativa do PITCIC.

Em **Estado-Maior**, selecione E1, E2, E3 ou E4 e clique em **Solicitar análise**. O resultado é uma tarefa de revisão documental. Examine e use **Aprovar** ou **Rejeitar**; **Atualizar** consulta a lista. Aprovar uma tarefa não executa manobras nem distribui apoio automaticamente. Não há agentes autônomos executando operações.

**Consultar tutor** solicita explicação pedagógica ao Ollama quando configurado. A tela identifica o modelo, evidências e incertezas ou informa o modo sem IA. O tutor não altera o estado, não aprova preparação, não comanda unidades e não recebe o PDF. O jogo funciona sem ele.

## 7. Avaliação e biblioteca

Em **Avaliação e biblioteca**, **Gerar APA descritiva** reúne dados e eventos registrados. Use-a para comparar a decisão tomada com o resultado das regras fictícias. Ela não comprova causalidade militar.

O painel probabilístico permite repetir a simulação abstrata do próximo turno e examinar sua distribuição sem alterar a partida. Isso é distinto da prévia exata do ciclo, que utiliza a semente específica da sessão.

A busca doutrinária consulta metadados locais; não contém manuais completos validados, nem garante edição vigente ou citação de página. Os cartões históricos de Monte Castelo, Waterloo e Batalha da Grã-Bretanha oferecem referências e resumos para estudo. Eles ainda não carregam cenários jogáveis nem reproduzem ordens de batalha ou combates reais. Links externos exigem internet.

## 8. Demonstração e limites

**Explorar demonstração completa** abre oito telas de mockup, separadas da partida persistente. Seus dados vivem na memória da página. Seus quatro turnos e variações ilustrativas não são as regras do motor integrado. Volte ao exercício para testar o fluxo real de 20 turnos.

Ainda não implementados: resolução de embates entre unidades, DAMEPLAN validado, extração automática de uma ordem em composição/posicionamento, rotas com custo de terreno, logística física, análise automática integrada dos quatro fatores PITCIC, cenários históricos executáveis e ambiente homologado para sigilo. Nenhum desses resultados deve ser inferido dos símbolos ou animações.

## 9. Conferência prática rápida

1. Crie uma partida e tente revisar antes de aprovar: deve aparecer o impedimento de preparação.
2. Preencha o exemplo, confira unidades e fatores e aprove.
3. Com clima normal, escolha destino permitido, verifique e enfileire: o símbolo ainda não deve mudar.
4. Revise, execute e confira turno 1, deslocamento e registro de evento.
5. Revise novamente; altere o clima antes de executar: será necessária nova revisão.
6. Use redução administrativa até prontidão de 25% ou menos e confirme bloqueio de novo deslocamento.
7. Entre com token de partido e confirme ausência dos controles de instrutor e informações globais.
8. Gere a APA e compare com os eventos. Saia e retome com identificador/token para conferir persistência.

## 10. Verificações de desenvolvimento

Na raiz do projeto:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
npm.cmd --prefix frontend run build
npm.cmd --prefix frontend run test:e2e -- --reporter=line
```

Os testes de navegador utilizam servidor separado na porta 18000 e banco temporário. Não devem utilizar nem apagar as partidas pessoais. A compilação verifica TypeScript e gera a interface servida pelo programa local.

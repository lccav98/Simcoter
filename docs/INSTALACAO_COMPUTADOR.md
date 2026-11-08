# SIMCOTER — Instalação no computador

**Situação:** versão experimental consolidada para teste **local**. O código está publicado, mas a compilação e os testes ainda não foram confirmados como aprovados. Não representa uma versão homologada.

## Antes de instalar

Um computador Windows 10/11 com conexão à internet na primeira instalação, espaço livre para Python e Node.js e acesso autorizado ao repositório privado. O navegador recomendado para o primeiro teste é Chrome ou Edge atual.

Instale, caso ainda não estejam disponíveis:

- [Python](https://www.python.org/downloads/) — versão 3.11 ou superior. No Windows, confirme que `py --version` funciona no Prompt de Comando.
- [Node.js LTS](https://nodejs.org/en/download) — inclui `npm`. Confirme `npm --version`.
- [Git](https://git-scm.com/downloads) — permite baixar o repositório privado. Será necessário autenticar o acesso ao GitHub.

## Primeira execução no Windows

Abra o Prompt de Comando e execute:

```cmd
git clone https://github.com/lccav98/Simcoter.git
cd Simcoter
INICIAR_SIMCOTER.cmd
```

O arquivo `INICIAR_SIMCOTER.cmd` verifica Python e npm, cria um ambiente virtual Python (`.venv`), instala as dependências gratuitas, compila a interface e inicia o servidor **somente no próprio computador**.

Quando aparecer `Abra: http://127.0.0.1:8000`, copie esse endereço para o Chrome ou Edge. **Mantenha a janela de execução aberta** enquanto usar o sistema.

Não é necessário instalar o Paperclip ou o Ollama para a primeira execução. Os quatro agentes E1–E4 funcionam por regras e produzem apenas revisões documentais. A biblioteca doutrinária ainda é parcial.

Se você já clonou o projeto anteriormente, primeiro execute `git pull` na pasta local, depois clique no arquivo `INICIAR_SIMCOTER.cmd` ou execute-o pelo terminal.

## Roteiro de verificação

1. Abrir `http://127.0.0.1:8000` e criar uma partida fictícia.
2. Guardar o token de instrutor quando for exibido.
3. Confirmar se o mapa MapLibre carrega, com controles de zoom e calungas.
4. Conferir o **indicador didático de prontidão** no calunga e na legenda.
5. Na área **Situação**, testar a revisão de prontidão com os botões `−20` e `+20`.
6. Na área **Planejamento**, alternar clima fictício entre normal, adverso e suspensão.
7. Testar as regras de terreno no tabuleiro: destino `(50, 30)` impeditivo e `(65, 65)` restritivo.
8. Confirmar que o sistema bloqueia ações não permitidas e exige autorização humana nas condições fictícias restritivas.
9. Solicitar as revisões documentais dos agentes E3 e E4.
10. Verificar a **Análise Pós-Ação**, incluindo os registros de mudanças ambientais e de disponibilidade.
11. Ativar áudio opcional e experimentar a prévia sintética, sem criar um evento de combate.

## Se não funcionar

- **Python não encontrado:** reinstalar ou verificar `py --version`.
- **npm não encontrado:** verificar a instalação do Node.js e reiniciar o Prompt de Comando.
- **Erro ao instalar pacotes:** manter a internet ativa na primeira execução e verificar se proxy ou firewall bloqueiam Python/npm.
- **Endereço indisponível:** deixar a janela do servidor aberta e confirmar se outra aplicação ocupa a porta 8000.
- **Mapa vazio:** conferir se Chrome/Edge oferece WebGL e se a rede permite carregar tiles OSM públicos.
- **Ollama não disponível:** comportamento esperado; o tutor apresenta fallback.
- **Erro no build ou testes:** registrar o texto do erro. A versão experimental pode exigir correções.

Para verificações adicionais:

```cmd
.venv\Scripts\python.exe -m pytest -q
cd frontend
npm run build
```

## Uso no iPad

O servidor local está configurado para `127.0.0.1` e **não é acessível pelo iPad**. Não alterar a configuração para `0.0.0.0` nem abrir a porta na LAN/internet sem implementar autenticação individual, HTTPS e revisão de segurança. O próximo incremento deverá contemplar uma versão hospedada/autenticada específica para Safari no iPad.

## Limitações e transparência

Todos os deslocamentos, terrenos, condições climáticas, níveis de prontidão e áreas são **completamente fictícios**. O mapa-base geográfico real não representa trafegabilidade nem avaliações militares, e o motor não calcula engajamentos ou poder de combate real. O movimento atualmente verifica **apenas o destino** em uma grade sintética; não há roteamento ou análise de percurso.

Referências técnicas:

- [Python — instalações oficiais](https://www.python.org/downloads/)
- [Node.js](https://nodejs.org/en/download)
- [Git](https://git-scm.com/downloads)
- [FastAPI](https://fastapi.tiangolo.com/)
- [MapLibre GL JS](https://maplibre.org/maplibre-gl-js/docs/)

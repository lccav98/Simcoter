# Validação Windows — 2026-11-08

Correções: imports e opções compatíveis com MapLibre 6; teste E4 atualizado para clima e indisponibilidade já previstos; Playwright usa o Python isolado no Windows e não reutiliza servidor desconhecido; inicializador usa npm.cmd e npm ci; dependências npm travadas e Vite atualizado.

Resultados reais:
- Python: 49 testes passaram (um aviso de depreciação Starlette/httpx).
- TypeScript e build Vite 8.3.6: passaram; aviso de bundle grande.
- npm audit após atualização: zero vulnerabilidades.
- Playwright Chromium: 3 testes de símbolos passaram; 5 testes visuais falharam ao iniciar navegador com spawn UNKNOWN, antes de carregar a aplicação.
- API iniciada pelo Playwright em 127.0.0.1:8000.
- JEV não disponível na sessão; não foi executado.

Executar no Windows com Python e Node instalados:
powershell -ExecutionPolicy Bypass -File scripts/run_local.ps1
Abrir http://127.0.0.1:8000 após a mensagem de inicialização.
Testes: .venv\Scripts\python.exe -m pytest -q
Em frontend: npx playwright install chromium webkit; npm run test:e2e

Pendências: solucionar lançamento dos navegadores e validar interface; WebKit/iPad; cartografia offline licenciada; IA local com modelo real. A base atual ainda usa tiles externos. Não houve integração de dados militares reais, alteração de permissões ou exposição em LAN/internet.

## Continuação validada
50 testes Python e 16 testes Playwright (Chromium headless e WebKit com viewport iPad) passaram. Corrigida perda de role nas respostas de mutação da API e teste de clima selecionando E3. Inicializador Windows executado até Uvicorn em 127.0.0.1:8000, com build e HTTP 200 confirmados. Corrigida saída silenciosa quando .venv já existia. Cartografia offline e Ollama real permanecem pendentes. WebKit não substitui teste em iPad físico.


Atualização: base sintética offline validada; 18 testes Playwright e 51 Python passaram. Consulte CARTOGRAFIA_OFFLINE.md. Banco de E2E agora isolado em diretório temporário e porta 18000.

Pacotes locais: build aprovado, 22 testes Playwright e 53 testes Python passaram. Diagnóstico Ollama executado: indisponível, geração real não validada. Importação limitada a linhas fictícias com metadados declarados de licença, sem upload ou persistência.

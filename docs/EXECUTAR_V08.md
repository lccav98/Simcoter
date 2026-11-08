# SIMCOTER 0.8 — executar o aplicativo integrado

**Estado:** implementação de integração publicada; validação de compilação no GitHub Actions e teste em Safari/iPad precisam ser realizados.

## Objetivo

Usar uma única origem HTTP local para a interface React/MapLibre e o backend
FastAPI, em vez de iniciar dois servidores. O mapa-base OpenStreetMap requer
internet. O motor de turnos, registro de relatórios, EMV, MPS e APA funcionam
localmente após a instalação de dependências, sem contratação de APIs externas.

## Pré-requisitos do computador que executa o servidor

- Python >= 3.10 com pip;
- Node.js >= 20 e npm;
- Git;
- Acesso autorizado ao repositório privado.

## Windows

No PowerShell, depois do clone do repositório:

```powershell
git clone https://github.com/lccav98/Simcoter.git
cd Simcoter
.\scripts\run_local.ps1
```

## Linux/macOS

```bash
git clone https://github.com/lccav98/Simcoter.git
cd Simcoter
bash scripts/run_local.sh
```

A preparação instala as dependências Python e Node, compila a interface e
executa o servidor em **http://127.0.0.1:8000**.

Depois da primeira instalação, basta executar `python scripts/start_local.py`
(ou `py scripts/start_local.py`, conforme o computador).

## Fluxo para verificar

1. Abrir `http://127.0.0.1:8000`.
2. Criar uma partida fictícia e guardar os tokens exibidos somente nessa criação.
3. Conferir o MapLibre: zoom +/−, deslocamento, escala, unidades fictícias.
4. Aprovar uma medida: o calco aprovado aparece sobre o mapa.
5. Registrar um relatório, avançar turnos e consultar MPS.
6. Solicitar análise do Estado-Maior Virtual E1–E4 e aprovar/rejeitar uma proposta.
7. Gerar a APA descritiva.
8. Consultar o tutor: com IA desabilitada, a interface apresenta o fallback.

## iPad — situação atual

**O iPad não executa automaticamente esse servidor Python.** A versão integrada
está preparada para uso em computador com navegador. Para acessá-la pelo
Safari do iPad será necessário disponibilizar um servidor autorizado por
uma origem HTTPS, com autenticação individual e segurança adequadas.
A versão 0.8 **não oferece** essas condições, portanto não se recomenda
abrir porta na LAN, criar um túnel público nem expor tokens em HTTP.

A demonstração HTML separada pode ser aberta em Safari, mas **não é a
aplicação React+FastAPI hospedada**.

## Limitações

- A aplicação ainda não usa cartas topográficas militares ou tiles offline.
- A base OSM pública serve para uso demonstrativo de baixo volume; não efetuar
  downloads em massa ou caches offline dela.
- Tokens de partida ainda são experimentais; o aplicativo não está homologado.
- Ollama é opcional e não é instalado automaticamente.
- Paperclip não está integrado; o EMV atual é baseado em regras.
- A compilação React/MapLibre e testes precisam de execução real no CI.

Referências: [FastAPI](https://fastapi.tiangolo.com/),
[MapLibre](https://maplibre.org/maplibre-gl-js/docs/),
[OSM tile usage](https://operations.osmfoundation.org/policies/tiles/).

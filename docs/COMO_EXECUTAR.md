# Como executar o primeiro protótipo

> Este é um **MVP didático individual**, não uma versão completa do SIMCOTER.
> Requer Python 3.10+, Node.js 20+ e npm. A instalação inicial das dependências exige acesso aos respectivos repositórios; depois, o protótipo básico pode operar sem internet, desde que tudo esteja previamente instalado.

## 1. Baixar o código

```bash
git clone https://github.com/lccav98/Simcoter.git
cd Simcoter
```

O repositório é privado: a conta precisa ter acesso para cloná-lo.

## 2. Iniciar API local

Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[test]'
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

Windows (PowerShell):

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[test]"
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

Testar saúde da API: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health). A documentação da API fica em [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

## 3. Iniciar interface

Em outro terminal, a partir da raiz do repositório:

```bash
cd frontend
npm install
npm run dev
```

Abrir [http://127.0.0.1:5173](http://127.0.0.1:5173).

O Vite encaminha chamadas `/api` para o serviço local na porta 8000. O estado da partida fica salvo no arquivo `data/simcoter.sqlite3`, ignorado pelo Git.

## 4. Testar

Na raiz do projeto, com ambiente Python ativado:

```bash
pytest -q
```

Na pasta `frontend`:

```bash
npm run build
```

## 5. Recursos implementados nesta etapa

- Criação e persistência de uma sessão individual;
- Mapa SVG sintético, símbolos ilustrativos e aprovação de duas medidas pré-definidas;
- Registro de relatórios fictícios, com origem, partido e turno;
- Progressão determinística dos indicadores logísticos abstratos;
- Acontecimentos condicionados à situação simulada e reprodutíveis;
- Geração de APA **descritiva**, vinculada aos eventos salvos.
- Catálogo local inicial de referências, somente metadados, com busca por termos.
- Propostas de problemas pedagógicos condicionadas a gatilhos objetivos da partida.

## 6. Limitações importantes

- **Não há IA implementada**, apesar de existir a previsão de integração local com Ollama.
- **Não há multijogador**, autenticação, separação real de dados entre partidos ou segurança para uso em redes compartilhadas.
- **Não há PWA offline instalável** nem integração com map.army/MapLibre neste estágio; o mapa é um SVG original, ilustrativo e sem georreferenciamento.
- Os parâmetros são puramente fictícios; não se trata de previsão militar ou reprodução do DAMEPLAN.
- Não expor a porta 8000 a redes externas. A API atual é exclusiva para desenvolvimento local.
- A APA não faz inferências estratégicas nem afirma causalidade além das regras registradas.

## 7. Próximos incrementos

Primeiro, endurecer os contratos de API, incluir autenticação, testes de acesso e separação por partido; depois, mapas locais com licença compatível, integração opcional Ollama e suporte à LAN com autorização por perfil.

Documentação de tecnologias: [FastAPI](https://fastapi.tiangolo.com/), [Vite](https://vite.dev/guide/), [pytest](https://docs.pytest.org/).

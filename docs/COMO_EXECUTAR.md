# Como executar o SIMCOTER

> Este é um **MVP didático individual**, não uma versão completa do SIMCOTER. Para iniciar frontend e API em uma só origem, prefira o guia [INSTALACAO_COMPUTADOR.md](INSTALACAO_COMPUTADOR.md), com o arquivo INICIAR_SIMCOTER.cmd no Windows. Complementos técnicos: [EXECUTAR_V08.md](EXECUTAR_V08.md) e [TERRENO_CLIMA_PRONTIDAO.md](TERRENO_CLIMA_PRONTIDAO.md).
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

- Criação e persistência de uma sessão individual; tokens de acesso por partida emitidos uma única vez ao instrutor.
- Mapa SVG sintético, símbolos ilustrativos e aprovação de duas medidas pré-definidas;
- Registro de relatórios fictícios, com origem, partido e turno;
- Progressão determinística dos indicadores logísticos abstratos;
- Acontecimentos condicionados à situação simulada e reprodutíveis;
- Geração de APA **descritiva**, vinculada aos eventos salvos.
- Catálogo local inicial de referências, somente metadados, com busca por termos.
- Propostas de problemas pedagógicos condicionadas a gatilhos objetivos da partida.
- Motor Probabilístico de Simulação (MPS) com eventos condicionados e efeitos abstratos, e painel de repetições Monte Carlo do próximo turno.
- Consulta `GET /api/sessions/{id}/probability?repetitions=500` não altera os dados da partida.
- Tutor opcional: `GET /api/sessions/{id}/ai/explanation`, com fallback sem IA e sem alteração de estado.
- Estado-Maior Virtual (EMV): painel E1–E4 para criar e aprovar tarefas de revisão documental. Consulte [ESTADO_MAIOR_VIRTUAL.md](ESTADO_MAIOR_VIRTUAL.md).

## 6. Limitações importantes

- **Há integração opcional de código com Ollama** para explicação didática, desativada por padrão; não foi validada com modelo real. Veja [TUTOR_IA_LOCAL.md](TUTOR_IA_LOCAL.md).
- **Não há multijogador pronto para uso em rede**. A versão 0.5 implementa tokens experimentais por partida e separação básica de respostas por partido, mas ainda não há autenticação individual, rotação de credenciais ou segurança homologada. Veja [ACESSO_E_PARTIDOS.md](ACESSO_E_PARTIDOS.md).
- **Não há PWA offline instalável** nem integração com map.army/MapLibre neste estágio; o mapa é um SVG original, ilustrativo e sem georreferenciamento.
- Os parâmetros são puramente fictícios; não se trata de previsão militar ou reprodução do DAMEPLAN.
- Não expor a porta 8000 a redes externas. A API atual é exclusiva para desenvolvimento local.
- A APA não faz inferências estratégicas nem afirma causalidade além das regras registradas.

## 7. Próximos incrementos

Próximas prioridades: autenticação individual, revogação de tokens, testes da versão 0.6, isolamento em LAN, integração opcional do modelo local com os agentes e avaliação de um adaptador Paperclip. Depois, cartografia offline licenciada.

Documentação de tecnologias: [FastAPI](https://fastapi.tiangolo.com/), [Vite](https://vite.dev/guide/), [pytest](https://docs.pytest.org/).

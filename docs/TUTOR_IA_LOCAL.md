# Tutor local Ollama — incremento 0.4

**Estado:** integração de código publicada. A execução com um modelo Ollama real e o pipeline CI ainda precisam ser verificados.

## Escopo

O tutor lê um **recorte estruturado** da partida fictícia e pode produzir um resumo educacional, achados vinculados a evidências e incertezas. Não altera recursos, eventos, turnos, decisões, ordens ou estado persistido. O motor probabilístico (MPS) permanece autônomo.

**Não há análise de combate real, seleção de alvos, planejamento de ataques ou aconselhamento operacional automatizado.**

## Ativação opcional — somente no próprio computador

1. Instale o Ollama a partir de [ollama.com](https://ollama.com/).
2. Baixe previamente um modelo compatível (exemplo de nome: `qwen3:4b`) conforme os requisitos de hardware, licença e disponibilidade.
3. Configure no terminal do backend:
   - `SIMCOTER_AI_ENABLED=true`
   - `SIMCOTER_OLLAMA_URL=http://127.0.0.1:11434`
   - `SIMCOTER_OLLAMA_MODEL=qwen3:4b`
4. Inicie o backend normalmente e abra a interface. Use o botão **Consultar tutor**.

No Windows PowerShell, por exemplo:

```powershell
$env:SIMCOTER_AI_ENABLED="true"
$env:SIMCOTER_OLLAMA_URL="http://127.0.0.1:11434"
$env:SIMCOTER_OLLAMA_MODEL="qwen3:4b"
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

No Linux/macOS:

```bash
export SIMCOTER_AI_ENABLED=true
export SIMCOTER_OLLAMA_URL=http://127.0.0.1:11434
export SIMCOTER_OLLAMA_MODEL=qwen3:4b
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

A instalação inicial de pacotes e modelos demanda acesso ao respectivo repositório de distribuição. Uma vez disponíveis localmente, o funcionamento não requer API em nuvem nem cobrança por tokens.

## API e validações

`GET /api/sessions/{id}/ai/explanation`

- **Desativada por padrão** (exige configuração explícita).
- Aceita somente `http://localhost` ou `http://127.0.0.1` como origem do Ollama; sem redirecionamentos HTTP.
- Usa formato JSON estruturado com campos `summary`, `findings` e `uncertainties`.
- Achados precisam referenciar identificadores de evidência existentes; saídas excessivas ou fora do contrato são descartadas.
- Resposta HTTP possui timeout de 20 segundos e limite de tamanho.
- Falhas devolvem `rules_fallback`, sem criar ou alterar registros.
- O prompt recebe apenas indicadores, eventos do motor, estados de medidas e número de relatórios. **Não recebe texto livre de relatórios.**

**Limitações:** o validador confirma formato e IDs, **não a veracidade semântica** das explicações. O modelo ainda pode interpretar equivocadamente evidências válidas. Não usar como fundamentação doutrinária sem trechos verificados. O próprio Ollama não é instalado pelo repositório.

## Segurança e isolamento

A partir da versão 0.5, a API exige token de instrutor para essa rota, mas ainda não há identidades individuais, revogação, criptografia em trânsito nem homologação de isolamento no multijogador. A síntese acessa um estado global do cenário, ainda que reduzido a metadados. **Nunca habilitar fora de localhost, em rede compartilhada ou com informações sensíveis.** Antes da implementação multijogador, criar visões de evidência por partido, autenticação, autorização, testes contra vazamento de dados e controle administrativo da IA.

## Testes

`pytest -q`

Os testes com cliente HTTP falso verificam fallback, validação dos IDs, restrições de origem local e ausência de texto livre no recorte. Não comprovam qualidade de um modelo real.

Referências técnicas: [Ollama API](https://docs.ollama.com/api), [Structured Outputs](https://docs.ollama.com/capabilities/structured-outputs), [FastAPI](https://fastapi.tiangolo.com/).

A conexão agora ignora proxies do sistema explicitamente. Serviço Ollama ausente na validação de 2026-11-08; testes automatizados não substituem execução com modelo real.

## Diagnóstico sem geração
Execute na raiz: `.venv\Scripts\python.exe scripts/check_local_ai.py`.
O diagnóstico consulta apenas /api/tags na origem local configurada, sem proxies, redirecionamentos, download de modelos ou conteúdo de partidas. Retorno 0: serviço respondeu e o nome exato do modelo configurado está instalado; 2: serviço respondeu, mas modelo não encontrado; 1: configuração ou serviço indisponível/inválido. Isso não valida a qualidade nem a geração de texto do modelo.

Validação atual: retorno 1, serviço indisponível. A IA continua opcional e desativada por padrão.

## Validação real — 2026-11-08
O serviço local foi encontrado com qwen3.5:4b instalado. O modelo padrão anterior (qwen3:4b) não estava instalado; selecione explicitamente o modelo disponível.

Teste real pela rota autenticada, em banco temporário: modo ollama_local, available=true, 2,22 segundos, estado inalterado. Acesso sem token retornou 401 e partido Azul retornou 403. Os 53 testes Python passaram após o ajuste.

A chamada agora solicita think=false, conforme https://ollama.com/blog/thinking. A primeira tentativa sem essa opção caiu em fallback por JSON inválido; a tentativa ajustada passou. O resultado continua sujeito a revisão: uma resposta chamou um indicador de 85 de "acima de 85", ilustrando que o contrato JSON não garante exatidão semântica.

Ativação no Windows:
~~~powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/run_local.ps1 -AIModel qwen3.5:4b
~~~
O parâmetro ativa a IA apenas no processo iniciado. Sem o parâmetro, permanece a configuração por variáveis de ambiente. Não instala nem baixa modelos.

Repetir teste real isolado:
~~~powershell
.venv\Scripts\python.exe scripts/test_local_ai.py --model qwen3.5:4b
~~~
O teste cria somente banco temporário e não imprime credenciais. Não mede qualidade geral do modelo nem autoriza aplicação operacional.

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

O backend atual não possui autenticação e não isola a consulta por partido. A síntese acessa um estado global do cenário, ainda que reduzido a metadados. **Nunca habilitar fora de localhost, em rede compartilhada ou com informações sensíveis.** Antes da implementação multijogador, criar visões de evidência por partido, autenticação, autorização, testes contra vazamento de dados e controle administrativo da IA.

## Testes

`pytest -q`

Os testes com cliente HTTP falso verificam fallback, validação dos IDs, restrições de origem local e ausência de texto livre no recorte. Não comprovam qualidade de um modelo real.

Referências técnicas: [Ollama API](https://docs.ollama.com/api), [Structured Outputs](https://docs.ollama.com/capabilities/structured-outputs), [FastAPI](https://fastapi.tiangolo.com/).

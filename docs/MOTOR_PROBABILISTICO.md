# MPS — Motor Probabilístico de Simulação

**Versão:** `mps-educacional-v1` — protótipo didático, não validado como modelo militar.

## Objetivo

Introduzir variabilidade reproduzível em eventos administrativos e logísticos
**fictícios**, sem depender do Jev, de APIs comerciais ou de IA generativa.
O MPS não estima resultados de combate, baixas, armamentos, engajamentos ou
probabilidades reais de vitória e derrota.

## Mecânica

1. No início do turno, cada indicador fictício diminui 2 pontos, com piso zero.
2. Eventos só são elegíveis quando o indicador associado está entre 1 e 85,
   após o desconto inicial. Se nenhum indicador estiver nessa faixa, o turno
   permanece rotineiro e **não há evento sorteado**.
3. Uma categoria elegível é selecionada por semente pseudoaleatória estável.
4. A severidade é sorteada conforme uma distribuição **hipotética**:
   - leve: 25% (variação adicional de até 1 ponto);
   - moderada: 50% (até 2 pontos);
   - acentuada: 25% (até 3 pontos).
5. O registro recebe regra, causa, categoria, severidade, número de alternativas
   elegíveis e efeito efetivamente aplicado, com piso zero.

Todos os números foram criados exclusivamente para demonstração de software.
Não foram extraídos do PPCOT, DAMEPLAN nem de capacidades militares reais.

## Repetibilidade e auditabilidade

O sorteio deriva de SHA-256 a partir de versão do modelo, semente, turno e
identificador da variável; não depende do relógio nem do estado global de
geradores de números aleatórios.

Duas partidas com parâmetros, decisões e sementes iguais evoluem da mesma
forma. Uma alteração nas regras exige mudança da versão do modelo, para evitar
misturar resultados de versões diferentes.

## Experimentação (Monte Carlo)

O endpoint:

`GET /api/sessions/{id}/probability?repetitions=500`

gera de 1 a 2.000 amostras do **próximo turno**, variando sementes de forma
reproduzível. Retorna contagens por categoria, severidade e médias de alteração
dos indicadores. **Não modifica o estado da partida.**

As contagens empíricas das amostras podem flutuar em torno das distribuições
configuradas; não representam previsões reais. O procedimento de variação de
sementes é uma ferramenta de análise pedagógica, não uma amostragem
cientificamente calibrada de eventos militares.

## Arquitetura

- `backend/app/probability.py`: transições puras, sorteios e projeções;
- `backend/app/game.py`: invocação no turno, persistência e APA;
- `backend/app/main.py`: rota estatística;
- `tests/test_probability.py`: propriedades e restrições.

A IA local futura poderá explicar os resultados, mas **não poderá editar
as probabilidades ou o estado da partida sem validação e aprovação**.

## Limitações e evolução

O protótipo ainda não possui controle de versão persistido no registro da
partida, editor de distribuições, cálculo de intervalos de confiança ou
simulações de muitos turnos. A futura interface do instrutor deverá deixar
claro o caráter hipotético dos valores. Não expor a API atual (sem autenticação)
a redes externas.

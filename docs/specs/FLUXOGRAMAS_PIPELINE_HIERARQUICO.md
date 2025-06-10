# 📊 Fluxogramas — Pipeline Hierárquico MLP (macro) + 2 PPO (micro)

## 1. Fluxograma de Treinamento

```
[ INÍCIO ]
   |
   v
[ Pré-processa dados (limpeza, features, sincronização TFs) ]
   |
   v
[ Rótulo macro: Gera labels (long, short, hold) para cada candle 1H ]
   |
   v
[ Engenharia de features macro ]
   |
   v
[ Treina MLP supervisionado para contexto macro ]
   |
   v
[ Salva MLP + scaler ]
   |
   v
+--------------------------+
| Para cada direção (long, short):    |
|    - Filtra dataset 5m onde MLP macro libera aquela direção
|    - Engenharia de features micro, concatena contexto macro como feature extra
|    - Cria ambiente RL (apenas allowed_actions da direção)
|    - Treina PPO (micro)
|    - Salva PPO, VecNormalize, logs |
+--------------------------+
   |
   v
[ Validação: Simula pipeline integrado em dados fora do sample ]
   |
   v
[ Analisa métricas (acurácia, drawdown, etc.), documenta e audita ]
   |
   v
[ FIM ]
```

---

## 2. Fluxograma de Execução/Inferência

```
[ INÍCIO ]
   |
   v
[ Coleta dados de mercado (1H e 5m), aplica limpeza/features ]
   |
   v
[ Carrega MLP (macro), PPO Long, PPO Short, scalers ]
   |
   v
[ A cada novo candle 1H ]
   |
   v
[ Extrai features macro, normaliza, envia para MLP ]
   |
   v
[ MLP decide: "long", "short", "hold" ]
   |
   v
+-------------------------------------------------+
| Para cada novo candle 5m:                       |
|   - Atualiza contexto macro atual               |
|   - Se MLP = "hold"   -> não opera (log "hold") |
|   - Se MLP = "long":                            |
|        -> ambiente long (PPO Long) recebe dados |
|        -> PPO Long decide ação (buy/hold)       |
|        -> Executa, loga resultado, aplica risco |
|   - Se MLP = "short":                           |
|        -> ambiente short (PPO Short) recebe     |
|        -> PPO Short decide ação (sell/hold)     |
|        -> Executa, loga resultado, aplica risco |
+-------------------------------------------------+
   |
   v
[ Logging detalhado: contexto macro, decisão, execução, métricas, erros ]
   |
   v
[ FIM ]
```

---

## Notas sobre rastreabilidade e integração

* Cada etapa crítica é logada e auditável.
* Ciclo macro→micro é explícito: não há decisão micro sem autorização macro.
* Validação/gestão de risco sempre aplicada após decisão micro.

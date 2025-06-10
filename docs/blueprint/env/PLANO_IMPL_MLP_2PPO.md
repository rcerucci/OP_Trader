# 🚦 Passo a Passo Prático — MLP (macro) + 2 PPO (micro)

## Fase 1 — Estruturação e Preparação

1. **Defina claramente o objetivo e métricas de sucesso**

   * Exemplo: aumentar taxa de acerto, reduzir drawdown, controlar risco, evitar overtrading no micro, etc.

2. **Separe datasets por timeframe**

   * Exporte/prepare dados 1H (macro) e 5m (micro), sempre sincronizados.
   * Certifique-se que as datas/barras estejam alinhadas (cuidado com fuso horário, buracos de dados, etc).

3. **Defina features relevantes**

   * Macro (1H): tendências, breakout, volatilidade, price action, indicadores, contexto.
   * Micro (5m): microestrutura, volume, candles, indicadores rápidos, volatilidade local, sinais do macro como feature extra.

4. **Planeje a arquitetura do pipeline**

   * Decisor MLP (macro) e 2 PPOs (micro).
   * Logging central, gestão de risco plugada, interface de teste/produção clara.

---

## Fase 2 — Construção do Decisor MLP (Macro)

5. **Rotule o dataset macro**

   * A cada barra 1H, defina se naquele contexto: operar long, short, hold (baseado em price action, expert labeling, resultado posterior, ou heurísticas inicialmente).

6. **Engenharia de features macro**

   * Teste diferentes combinações, faça validação cruzada, verifique importância das features.
   * Padronize a normalização dos dados (StandardScaler, MinMaxScaler, etc).

7. **Treine e valide o MLP**

   * Faça split treino/teste temporal (evite “vazar” dados futuros).
   * Avalie as métricas: acurácia, recall, F1 para cada classe, confusão entre regimes.
   * Salve modelo e scaler para uso futuro.

---

## Fase 3 — Treinamento dos PPOs (Micro)

8. **Crie ambientes RL (micro)**

   * Um ambiente para cada direção (long e short), ambos recebendo contexto macro como feature adicional.
   * Valide que as ações permitidas no ambiente estejam corretas (“long only” ou “short only”).

9. **Treine cada PPO separadamente**

   * Use apenas os períodos em que o decisor macro rotulou “permitido operar long” para PPO long, e “permitido operar short” para PPO short.
   * Use wrappers como VecNormalize para normalização online.
   * Monitore convergência, reward, drawdown, comportamento fora do sample.

10. **Salve modelos, normalizadores e logs**

    * Para cada PPO, salve policy, scaler, checkpoints, métricas de treino.

---

## Fase 4 — Integração e Teste do Pipeline

11. **Integre pipeline decisor+PPOs**

    * A cada step, MLP macro recebe o contexto atual (1H) e “libera” direção ou hold.
    * Se liberado, PPO micro correspondente gera ação/timing.
    * Mantenha logs detalhados das decisões do MLP e das execuções dos PPOs.

12. **Simule um período “fora do sample”**

    * Execute o pipeline integrado em histórico nunca visto, salve todas as decisões, trades, métricas, logs e erros.

13. **Analise resultados**

    * Taxa de acerto, drawdown, net profit, sharp, razão trades/hold, quantidade de operações evitadas pelo decisor.

14. **Refine, retreine e documente**

    * Identifique falhas: timing ruim? contexto macro falha? PPOs pouco responsivos? Ajuste o que for necessário.

---

## Fase 5 — Deploy e Monitoramento

15. **Prepare deploy para produção ou forward test**

    * Garanta versionamento dos modelos (MLP+PPOs), dos scalers e da configuração.
    * Implemente “safety switches” (limites de perda diária, bloqueio de ordens incoerentes, logs redundantes).

16. **Implemente monitoramento**

    * Logging automático das decisões e execuções, alertas em caso de desvios de risco/performance, dashboards de acompanhamento (pode começar em planilha/logs CSV).

17. **Audite periodicamente**

    * Analise logs, acurácia do decisor, performance dos PPOs, casos de erro/stop, drawdown e se o macro está realmente “filtrando” bem os sinais do micro.

---

# ✅ Checklist de Riscos e Custos

| Risco/Custo                              | Mitigação                                             |
| ---------------------------------------- | ----------------------------------------------------- |
| **Rotulagem do macro ruim**              | Validação cruzada, revisão manual/semiautomática      |
| **PPOs não convergem**                   | Testar hiperparâmetros, aumentar dados, simplificar   |
| **Lookahead bias (vazamento futuro)**    | Split temporal rigoroso, nunca usar dados do futuro   |
| **Pipeline quebrado por timeframes**     | Sincronização rigorosa, validação contínua            |
| **Overfitting do MLP ou PPO**            | Regularização, augmentação, early stopping, backtest  |
| **Desalinhamento macro↔micro**           | Logging, auditoria, simulação antes de live           |
| **Latência e delays no real**            | Testes forward, validação em ambiente simulado real   |
| **Manutenção de múltiplos modelos**      | Versionamento, documentação clara, scripts de deploy  |
| **Risco operacional (black swan, bugs)** | “Safety switches”, limites de risco, logs redundantes |
| **Falta de interpretabilidade**          | Logging detalhado, métricas claras, análise ex-post   |

---

# 🎯 Resumo visual

```text
DATA (1H, 5m)
   ↓
MLP DECISOR (macro)
   ↓    |------ Não operar (hold) → ignora PPOs
   |    |------ Long liberado → PPO Long executa trade
   |    |------ Short liberado → PPO Short executa trade
   ↓
Ambiente RL/Execução
   ↓
Gestão de Risco + Logging
```

---

Esse ciclo cobre desde a preparação de dados até o deploy e operação auditável — balanceando robustez, modularidade e complexidade viável para um time pequeno.

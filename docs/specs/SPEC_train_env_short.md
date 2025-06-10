# SPEC\_train\_env\_short.md — src/env/environments/train\_env\_short.py

---

## 1. Objetivo e Contexto

Ambiente RL especializado para treinamento de estratégias short-only ("sell"/"hold") no pipeline Op\_Trader. Herda contrato do BaseEnv, restringe ações possíveis e integra componentes plugáveis (risco, posição, reward, logger) para simulação, backtest e validação de modelos PPO voltados a operações de venda.

---

## 2. Entradas e Assinatura

| Parâmetro          | Tipo   | Obrigatório | Descrição                              | Exemplo                      |
| ------------------ | ------ | ----------- | -------------------------------------- | ---------------------------- |
| context\_macro     | dict   | Não         | Contexto macro (direção, regime, etc.) | {"direction": "short"}       |
| position\_manager  | obj    | Não         | Plug-in de posições                    | DummyPositionManager()       |
| risk\_manager      | obj    | Não         | Plug-in de risco                       | DummyRiskManager()           |
| reward\_aggregator | obj    | Não         | Plug-in de reward                      | DummyRewardAggregator()      |
| logger             | Logger | Não         | Logger estruturado                     | get\_logger("TrainEnvShort") |
| debug              | bool   | Não         | Logging detalhado                      | True                         |
| action             | int    | Step        | Índice da ação (“sell”=0, “hold”=1)    | 0                            |

**Assinatura dos métodos:**

```python
class TrainEnvShort(BaseEnv):
    def __init__(self, context_macro: dict = None, **kwargs): ...
    def step(self, action: int): ...
    def reset(self, *, context_macro=None, seed=None, options=None): ...
```

---

## 3. Saídas e Retornos

| Método | Retorno                                  | Descrição                                              |
| ------ | ---------------------------------------- | ------------------------------------------------------ |
| reset  | obs, info                                | Observação inicial e info do reset                     |
| step   | obs, reward, terminated, truncated, info | Step completo, delegação plugável, logging, edge cases |

---

## 4. Fluxo de Execução

* ****init**:** Herdado do BaseEnv, restringe allowed\_actions=\["sell", "hold"].
* **reset:** Atualiza contexto macro se informado, delega para reset do BaseEnv, logging estruturado.
* **step:** Aceita apenas ações válidas (0="sell", 1="hold"). Se ação inválida, aplica penalidade, encerra episódio e loga erro crítico. Chama step do BaseEnv para integração plugável.

---

## 5. Edge Cases e Validações

* Ação inválida: penalidade padrão, log crítico, encerra episódio
* Contexto macro ausente/atualização dinâmica: fallback seguro
* Plug-ins obrigatórios ausentes: warning, fallback
* Falha em plug-ins: log warning, execução não é interrompida

---

## 6. Integração e Compatibilidade

* Herda de BaseEnv, plugável em qualquer pipeline RL Op\_Trader
* Usa get\_logger (logging\_utils), integra com PositionManager, RiskManager, RewardAggregator
* Compatível com pytest e produção

---

## 7. Docstring Google Style

```python
class TrainEnvShort(BaseEnv):
    """
    Ambiente RL especializado para estratégias short-only (sell/hold) no Op_Trader.

    Métodos principais:
      - reset: inicializa episódio/contexto macro, delega ao BaseEnv.
      - step: aceita apenas ações sell/hold, delega ao BaseEnv, logging e edge cases.

    Args:
        context_macro (dict, opcional): Contexto macro.
        position_manager (obj, opcional): Plug-in de posição.
        risk_manager (obj, opcional): Plug-in de risco.
        reward_aggregator (obj, opcional): Plug-in de reward.
        logger (Logger, opcional): Logger estruturado.
        debug (bool): Logging detalhado.
    """
    ...
```

---

## 8. Exemplo de Uso

```python
from src.env.environments.train_env_short import TrainEnvShort
from src.utils.logging_utils import get_logger

logger = get_logger("TrainEnvShort")
env = TrainEnvShort(context_macro={"direction": "short"}, logger=logger, debug=True)
obs, info = env.reset()
obs, reward, terminated, truncated, info = env.step(0)  # sell
```

---

## 9. Testes e Validação

* Cobertura unitária dos métodos (reset, step, edge cases, integração plugável)
* Testes recomendados:

```bash
pytest tests/unit/test_train_env_short.py -v -s --log-cli-level=DEBUG
```

* Homologação inclui: step (sell/hold), ação inválida, logging, contexto macro dinâmico, mocks de risk/position/reward

---

## 10. Checklist de Qualidade

* [x] Docstrings Google Style, código PEP8
* [x] Logging detalhado, rastreável
* [x] Edge cases (ação inválida, contexto macro, plug-ins)
* [x] Testes unitários e integração, mock de plug-ins
* [x] Compatível com produção e pipelines RL
* [x] Exemplo validado e testado

---

## 11. Rastreabilidade e Histórico

* DEVELOP\_TABLE.md: linha TrainEnvShort, src/env/environments/train\_env\_short.py, @CODE (marcar @STABLE ao final do ciclo environments)
* REFERENCE\_TABLE.md: a ser movido após o ciclo completo
* DEV\_LOG.md: ciclo 2025-06-08 homologado, todos os testes unitários e integração passaram
* TESTE: tests/unit/test\_train\_env\_short.py
* SPEC\_TEMPLATE.md: v2.0
* Última atualização: 2025-06-08
* Autor: Equipe Op\_Trader

---

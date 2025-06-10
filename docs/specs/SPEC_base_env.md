# SPEC\_base\_env.md — src/env/environments/base\_env.py

---

## 1. Objetivo e Contexto

Ambiente RL base universal para o pipeline Op\_Trader, utilizado como contrato padrão para todos os ambientes específicos (long, short, etc.).
Garante integração plugável com componentes de logging, gestão de risco, observação, validação e contexto macro, viabilizando tanto RL puro quanto pipelines hierárquicos (MLP macro + PPO micro).

---

## 2. Entradas e Assinatura

| Parâmetro          | Tipo       | Obrigatório | Descrição                              | Exemplo                 |
| ------------------ | ---------- | ----------- | -------------------------------------- | ----------------------- |
| allowed\_actions   | list\[str] | Sim         | Lista de ações permitidas              | \["buy", "hold"]        |
| context\_macro     | dict       | Não         | Contexto macro (direção, regime, etc.) | {"direction": "long"}   |
| risk\_manager      | obj        | Não         | Gerenciador de risco plugável          | DummyRiskManager()      |
| position\_manager  | obj        | Não         | Gerenciador de posições plugável       | DummyPositionManager()  |
| reward\_aggregator | obj        | Não         | Agregador de recompensas plugável      | DummyRewardAggregator() |
| logger             | Logger     | Não         | Logger estruturado                     | get\_logger("BaseEnv")  |
| debug              | bool       | Não         | Ativa logs detalhados                  | True                    |
| action             | int        | Step        | Índice da ação a ser executada         | 0                       |

**Assinatura dos métodos:**

```python
class BaseEnv(gym.Env):
    def __init__(self, allowed_actions: list[str], context_macro: dict = None, risk_manager=None, position_manager=None, reward_aggregator=None, logger=None, debug: bool = False, **kwargs): ...
    def reset(self, *, context_macro: dict = None, seed: int = None, options: dict = None) -> tuple: ...
    def step(self, action) -> tuple: ...
    def set_context_macro(self, context_macro: dict): ...
    def get_logs(self) -> dict: ...
    def render(self, mode='human'): ...
    def close(self): ...
```

---

## 3. Saídas e Retornos

| Método              | Retorno                                  | Descrição                                               |
| ------------------- | ---------------------------------------- | ------------------------------------------------------- |
| reset               | obs, info                                | Observação inicial e info do reset                      |
| step                | obs, reward, terminated, truncated, info | Step completo, delegação plugável, logging e edge cases |
| set\_context\_macro | None                                     | Atualiza contexto macro dinamicamente                   |
| get\_logs           | dict                                     | Retorna todos logs acumulados                           |
| render              | None                                     | Implementação opcional (filhos)                         |
| close               | None                                     | Garante flush/fechamento de recursos                    |

---

## 4. Fluxo de Execução

* ****init**:** Inicializa ações permitidas, contexto macro, plug-ins de gestão e logger.
* **reset:** Atualiza contexto macro, inicia episódio, gera observação inicial, loga contexto e estado.
* **step:** Valida ação, delega risk/position/reward, loga resultado, retorna tupla padrão RL.
* **set\_context\_macro:** Permite alteração dinâmica do contexto macro.
* **get\_logs:** Retorna todos os logs de episódios.
* **render/close:** Prontos para override/expansão.

---

## 5. Edge Cases e Validações

* Ação inválida: penalidade padrão, log crítico, encerra episódio
* Contexto macro ausente ou inválido: fallback seguro
* Plug-ins obrigatórios ausentes: warning, fallback
* Falha em plug-ins: log warning, execução não é interrompida

---

## 6. Integração e Compatibilidade

* Herda de gymnasium.Env, plugável em qualquer pipeline RL do Op\_Trader
* Usa get\_logger (logging\_utils), integra com PositionManager, RiskManager, RewardAggregator
* Compatível com pytest e produção

---

## 7. Docstring Google Style

```python
class BaseEnv(gym.Env):
    """
    Ambiente RL base universal para Op_Trader. Contrato para ambientes customizados.

    Métodos principais:
      - reset: inicializa episódio e contexto macro.
      - step: valida ação, delega plug-ins, retorna step RL.
      - set_context_macro: atualiza contexto macro.
      - get_logs: retorna todos logs.
      - render/close: override para filhos.

    Args:
        allowed_actions (list[str]): Ações permitidas.
        context_macro (dict, opcional): Contexto macro.
        risk_manager (obj, opcional): Plug-in de risco.
        position_manager (obj, opcional): Plug-in de posição.
        reward_aggregator (obj, opcional): Plug-in de reward.
        logger (Logger, opcional): Logger estruturado.
        debug (bool): Logging detalhado.
    """
    ...
```

---

## 8. Exemplo de Uso

```python
from src.env.environments.base_env import BaseEnv
from src.utils.logging_utils import get_logger

logger = get_logger("TrainEnvLong")
env = BaseEnv(allowed_actions=["buy", "hold"], context_macro={"direction": "long"}, logger=logger, debug=True)
obs, info = env.reset()
obs, reward, terminated, truncated, info = env.step(0)
```

---

## 9. Testes e Validação

* Cobertura unitária dos métodos (reset, step, set\_context\_macro, get\_logs, edge cases, integração plugável)
* Testes recomendados:

```bash
pytest tests/unit/test_base_env.py -v -s --log-cli-level=DEBUG
```

* Homologação inclui: step/ação válida, ação inválida, contexto macro dinâmico, mocks de risk/position/reward, logging

---

## 10. Checklist de Qualidade

* [x] Docstrings Google Style, código PEP8
* [x] Logging detalhado, rastreável e thread-safe
* [x] Edge cases (ação inválida, contexto macro, plug-ins)
* [x] Testes unitários e integração, mock de plug-ins
* [x] Compatível com produção e pipelines RL
* [x] Exemplo validado e testado

---

## 11. Rastreabilidade e Histórico

* DEVELOP\_TABLE.md: linha BaseEnv, src/env/environments/base\_env.py, @CODE (marcar @STABLE ao final do ciclo environments)
* REFERENCE\_TABLE.md: a ser movido após o ciclo completo
* DEV\_LOG.md: ciclo 2025-06-08 homologado, todos os testes unitários e integração passaram
* TESTE: tests/unit/test\_base\_env.py
* SPEC\_TEMPLATE.md: v2.0
* Última atualização: 2025-06-08
* Autor: Equipe Op\_Trader

---

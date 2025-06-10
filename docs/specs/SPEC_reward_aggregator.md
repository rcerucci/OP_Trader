# SPEC\_reward\_aggregator.md — src/env/env\_libs/reward\_aggregator.py

---

## 1. Objetivo e Contexto

O módulo **RewardAggregator** centraliza o cálculo, agregação e customização de recompensas em ambientes RL do Op\_Trader. Permite combinar múltiplos componentes de reward (lucro, risco, penalidades, custos, drawdown, etc.), aplicar pesos, normalização, clipping e regras plugáveis para adaptar a política de incentivo de acordo com o ambiente, regime ou estratégia. Garante logging e auditoria detalhada do cálculo, além de integração transparente com demais módulos do pipeline.

---

## 2. Entradas e Assinatura

| Parâmetro          | Tipo   | Obrigatório | Descrição                                     | Exemplo                          |
| ------------------ | ------ | ----------- | --------------------------------------------- | -------------------------------- |
| reward\_components | list   | Não         | Lista de tuplas (name, func) ou funções       | \[("profit\_reward", func), ...] |
| weights            | dict   | Não         | Pesos aplicados a cada componente             | {"profit\_reward": 0.7, ...}     |
| normalization      | str    | Não         | Método de normalização ("z\_score", "minmax") | "z\_score"                       |
| logger             | Logger | Não         | Logger estruturado padrão Op\_Trader          | get\_logger("RewardAggregator")  |
| debug              | bool   | Não         | Ativa logs detalhados                         | True                             |
| state\_before      | dict   | Sim         | Estado antes da ação                          | {"portfolio\_value": 100.0}      |
| action             | dict   | Sim         | Ação executada                                | {"type": "buy"}                  |
| state\_after       | dict   | Sim         | Estado após a ação                            | {"portfolio\_value": 110.0}      |
| name               | str    | Sim         | Nome do componente customizado                | "custom"                         |
| func               | func   | Sim         | Função callable de cálculo de reward          | lambda s0, a, s1: ...            |
| weight             | float  | Não         | Peso do componente customizado                | 1.0                              |
| path               | str    | Não         | Diretório destino para salvar breakdown       | "logs/audits/"                   |

**Assinatura dos métodos:**

```python
class RewardAggregator:
    def __init__(self, reward_components: list = None, weights: dict = None, normalization: str = None, logger=None, debug: bool = False, **kwargs): ...
    def calculate_reward(self, state_before: dict, action: dict, state_after: dict) -> float: ...
    def get_reward_breakdown(self) -> dict: ...
    def add_component(self, name: str, func, weight: float = 1.0): ...
    def reset(self): ...
    def save_breakdown(self, path: str = None): ...
```

---

## 3. Saídas e Retornos

| Método                 | Retorno | Descrição                                                             |
| ---------------------- | ------- | --------------------------------------------------------------------- |
| calculate\_reward      | float   | Reward total (agregado, normalizado se configurado)                   |
| get\_reward\_breakdown | dict    | Detalhamento do cálculo da última reward (componentes, pesos, normed) |
| add\_component         | None    | Adiciona componente customizado (nome, função, peso)                  |
| reset                  | None    | Limpa histórico e breakdown acumulados                                |
| save\_breakdown        | None    | Salva breakdown detalhado em CSV/JSON                                 |

---

## 4. Fluxo de Execução

* calculate\_reward: chama cada componente (nomeado), aplica peso, soma/agrega, normaliza (z\_score/minmax/none), logging detalhado e breakdown.
* get\_reward\_breakdown: retorna o breakdown do último cálculo (componentes, valores, pesos, total, normed).
* add\_component: permite adicionar dinamicamente (nome, função, peso) ao pipeline de reward.
* reset: limpa histórico de rewards e breakdown.
* save\_breakdown: salva breakdown detalhado da reward mais recente, via file\_saver (logs/audits/).

---

## 5. Edge Cases e Validações

* Componente retorna NaN/erro: log WARNING, substitui por zero.
* Soma de pesos diferente de 1: log WARNING, normaliza/informa.
* Normalização inválida: fallback para "none".
* Função inválida/exception: log ERROR, valor zero, componente removido se necessário.
* Parâmetro inválido: log ERROR, ValueError.
* Thread safety em todos os métodos críticos.

---

## 6. Integração e Compatibilidade

* Usa get\_logger, build\_filename, save\_dataframe (utils Op\_Trader).
* Plugável com PositionManager, RiskManager, TradeLogger, BaseEnv, TrainEnvLong/Short.
* Testes usam tmp\_path do pytest; produção usa logs/audits/.
* Edge cases de nome/tuple cobertos (compatível com tupla ou função direta).

---

## 7. Docstring Google Style

```python
class RewardAggregator:
    """
    Centraliza cálculo, agregação e logging de recompensas (reward) para ambientes RL Op_Trader.

    Métodos principais:
      - calculate_reward: calcula reward total agregando componentes.
      - get_reward_breakdown: detalhamento da última reward calculada.
      - add_component: adiciona componente customizado.
      - reset: limpa histórico e breakdown.
      - save_breakdown: salva breakdown detalhado em CSV/JSON.

    Args:
        reward_components (list): Lista de tuplas (name, func) ou funções.
        weights (dict): Pesos de cada componente.
        normalization (str): Método de normalização ("z_score", "minmax", "none").
        logger (Logger, opcional): Logger estruturado.
        debug (bool): Ativa logs detalhados.
    """
    ...
```

---

## 8. Exemplo de Uso

```python
from src.env.env_libs.reward_aggregator import RewardAggregator
from src.utils.logging_utils import get_logger

def profit_reward(state_before, action, state_after):
    return state_after['portfolio_value'] - state_before['portfolio_value']

def drawdown_penalty(state_before, action, state_after):
    return -abs(state_after.get('drawdown', 0))

logger = get_logger("RewardAggregator", debug=True)
ra = RewardAggregator(
    reward_components=[('profit_reward', profit_reward), ('drawdown_penalty', drawdown_penalty)],
    weights={"profit_reward": 0.8, "drawdown_penalty": 0.2},
    normalization="z_score",
    logger=logger
)

reward = ra.calculate_reward(state_before, action, state_after)
breakdown = ra.get_reward_breakdown()
print(reward, breakdown)
ra.save_breakdown()
```

---

## 9. Testes e Validação

* Cobertura unitária dos métodos (cálculo, composição, adição dinâmica, edge case, persistência, reset)
* Testes usam tmp\_path do pytest, produção salva em logs/audits/
* Comando recomendado:

```bash
pytest tests/unit/test_reward_aggregator.py -v -s --log-cli-level=DEBUG
```

---

## 10. Checklist de Qualidade

* [x] Código PEP8, docstrings Google, imports absolutos
* [x] Logging detalhado, auditável e thread-safe
* [x] Edge cases (tuple/nome/erro/NaN)
* [x] Testes unitários e integração
* [x] Compatível com produção (logs/audits/) e testes (tmp\_path)

---

## 11. Rastreabilidade e Histórico

* DEVELOP\_TABLE.md: \[linha correspondente]
* REFERENCE\_TABLE.md: \[finalizar ciclo]
* DEV\_LOG.md: \[entrada do ciclo]
* TESTE: tests/unit/test\_reward\_aggregator.py
* SPEC\_TEMPLATE.md: v2.0
* Última atualização: 2025-06-08
* Autor: Equipe Op\_Trader

---

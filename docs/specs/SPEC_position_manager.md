# SPEC\_position\_manager.md — src/env/env\_libs/position\_manager.py

---

## 1. Objetivo e Contexto

O módulo **PositionManager** centraliza a gestão de posições dos ambientes RL do Op\_Trader, incluindo abertura, fechamento, ciclo (open/close/increase/reduce), integração com RiskManager e persistência de snapshots. Garante controle thread-safe, logging estruturado, rejeição de parâmetros inválidos, rastreio de eventos e pronta integração com TradeLogger e RewardAggregator. Serve de base para qualquer ambiente RL/ML onde a posição precisa ser controlada de forma robusta.

---

## 2. Entradas e Assinatura

| Parâmetro     | Tipo   | Obrigatório | Descrição                                | Exemplo                        |
| ------------- | ------ | ----------- | ---------------------------------------- | ------------------------------ |
| symbol        | str    | Sim         | Ativo negociado                          | "EURUSD"                       |
| risk\_manager | obj    | Não         | Instância de RiskManager para validação  | RiskManager()                  |
| logger        | Logger | Não         | Logger estruturado padrão Op\_Trader     | get\_logger("PositionManager") |
| debug         | bool   | Não         | Ativa logs detalhados                    | True                           |
| action        | str    | Sim         | Ação da posição (buy/sell/open/close)    | "buy"                          |
| price         | float  | Sim         | Preço de execução                        | 1.105                          |
| size          | float  | Sim         | Quantidade de ativos                     | 1.0                            |
| context       | dict   | Não         | Contexto adicional (regime, SL/TP, etc.) | {"drawdown": 0.1, ...}         |
| path          | str    | Não         | Caminho para salvar snapshot             | "logs/audits/"                 |

**Assinatura dos métodos:**

```python
class PositionManager:
    def __init__(self, symbol: str, risk_manager=None, logger=None, debug: bool = False, **kwargs): ...
    def open_position(self, action: str, price: float, size: float, context: dict = None) -> dict: ...
    def close_position(self, price: float, context: dict = None) -> dict: ...
    def get_current_position(self) -> dict: ...
    def manage_position(self, action: str, price: float, size: float, context: dict = None) -> dict: ...
    def reset(self): ...
    def save_snapshot(self, path: str = None): ...
```

---

## 3. Saídas e Retornos

| Método                 | Retorno      | Descrição                                                          |
| ---------------------- | ------------ | ------------------------------------------------------------------ |
| open\_position         | dict         | Status/result da abertura (aberta/rejeitada, motivo, estado atual) |
| close\_position        | dict         | Status/result do fechamento (fechada/erro, PnL, snapshot)          |
| get\_current\_position | dict ou None | Snapshot da posição aberta (ou None)                               |
| manage\_position       | dict         | Resultado da operação (open/close/increase/reduce)                 |
| reset                  | None         | Limpa posição e histórico acumulado                                |
| save\_snapshot         | None         | Salva histórico de eventos/posição em CSV para auditoria           |

---

## 4. Fluxo de Execução

* open\_position: valida parâmetros e risco, rejeita se já existe posição, registra evento.
* close\_position: fecha posição ativa, calcula PnL, atualiza risco, registra evento.
* get\_current\_position: retorna snapshot atual (thread-safe).
* manage\_position: ciclo de posição (open, close, outros futuros).
* reset: limpa histórico e posição ativa para novo ciclo/episódio.
* save\_snapshot: salva histórico de eventos e posições (CSV).

---

## 5. Edge Cases e Validações

* Tentativa de abrir com posição já aberta: log CRITICAL, rejeita.
* Parâmetros inválidos (price, size, action): log ERROR, raise ValueError.
* Fechamento sem posição aberta: log WARNING, ignora.
* Integração RiskManager: rejeição de ordens, atualização de métricas.
* Thread safety garantido via `threading.RLock()`.

---

## 6. Integração e Compatibilidade

* Usa get\_logger, build\_filename, save\_dataframe do projeto.
* Plugável com RiskManager, TradeLogger, RewardAggregator, BaseEnv, TrainEnvLong/Short.
* Testes usam tmp\_path do pytest; produção usa logs/audits/.

---

## 7. Docstring Google Style

```python
class PositionManager:
    """
    Gerencia posição aberta, execução, fechamento e snapshot, com controle thread-safe.

    Métodos principais:
      - open_position: abertura de posição com validação de risco.
      - close_position: fechamento, cálculo de PnL, atualização de risco.
      - get_current_position: snapshot da posição ativa.
      - manage_position: ciclo de posição (open, close, etc.).
      - reset: limpa posição e histórico.
      - save_snapshot: salva histórico para auditoria.

    Args:
        symbol (str): Ativo negociado.
        risk_manager (obj, opcional): Instância para validação de risco.
        logger (Logger, opcional): Logger estruturado.
        debug (bool): Ativa logs detalhados.
    """
    ...
```

---

## 8. Exemplo de Uso

```python
from src.env.env_libs.position_manager import PositionManager
from src.env.env_libs.risk_manager import RiskManager
from src.utils.logging_utils import get_logger

logger = get_logger("PositionManager", debug=True)
rm = RiskManager(logger=logger)
pm = PositionManager(symbol="EURUSD", risk_manager=rm, logger=logger)
res = pm.open_position("buy", 1.10, 1.0)
print(res)
res2 = pm.close_position(1.12)
print(res2)
pm.save_snapshot()
```

---

## 9. Testes e Validação

* Cobertura unitária dos métodos (abertura, fechamento, rejeição, histórico, integração)
* Testes usam tmp\_path do pytest, produção salva em logs/audits/
* Comando recomendado:

```bash
pytest tests/unit/test_position_manager.py -v -s --log-cli-level=DEBUG
```

---

## 10. Checklist de Qualidade

* [x] Código PEP8, docstrings Google, imports absolutos
* [x] Logging detalhado, auditável e thread-safe (RLock)
* [x] Edge cases e rejeição segura (param, duplo open, reset, risk)
* [x] Testes unitários e integração
* [x] Compatível com produção (logs/audits/) e testes (tmp\_path)

---

## 11. Rastreabilidade e Histórico

* DEVELOP\_TABLE.md: \[linha correspondente]
* REFERENCE\_TABLE.md: \[finalizar ciclo]
* DEV\_LOG.md: \[entrada do ciclo]
* TESTE: tests/unit/test\_position\_manager.py
* SPEC\_TEMPLATE.md: v2.0
* Última atualização: 2025-06-08
* Autor: Equipe Op\_Trader

---

# SPEC\_risk\_manager.md — src/env/env\_libs/risk\_manager.py

---

## 1. Objetivo e Contexto

O módulo **RiskManager** centraliza a lógica de gestão de risco dos ambientes RL do Op\_Trader, incluindo validação de ordens, limites dinâmicos de exposição, sizing, drawdown, SL/TP, atualização de métricas de risco, e geração de snapshots auditáveis. Garante proteção do portfólio, rastreabilidade e flexibilidade (configuração externa via YAML/JSON ou defaults seguros). Compatível com operações reais e simuladas, multi-ativos, e plugável em todos os ambientes RL.

---

## 2. Entradas e Assinatura

| Parâmetro     | Tipo   | Obrigatório | Descrição                                 | Exemplo                       |
| ------------- | ------ | ----------- | ----------------------------------------- | ----------------------------- |
| config\_path  | str    | Não         | Caminho do arquivo de config YAML/JSON    | "configs/risk\_config.yaml"   |
| logger        | Logger | Não         | Logger estruturado padrão Op\_Trader      | get\_logger("RiskManager")    |
| debug         | bool   | Não         | Ativa logs detalhados                     | True                          |
| symbol        | str    | Sim         | Ativo para validação/controle             | "EURUSD"                      |
| action        | str    | Sim         | Ação desejada                             | "buy"                         |
| size          | float  | Sim         | Tamanho da ordem/posição                  | 1.0                           |
| price         | float  | Sim         | Preço da ordem                            | 1.105                         |
| context       | dict   | Não         | Contexto adicional (drawdown, SL/TP, ...) | {"drawdown": 0.1, ...}        |
| position      | dict   | Sim         | Info da posição para checagem de limites  | {"drawdown": 0.2, ...}        |
| trade\_result | dict   | Sim         | Resultado de trade (pnl, drawdown, ...)   | {"pnl": 10, "drawdown": 0.01} |
| path          | str    | Não         | Caminho para salvar snapshot              | "logs/audits/"                |

**Assinatura dos métodos:**

```python
class RiskManager:
    def __init__(self, config_path: str = None, logger=None, debug: bool = False, **kwargs): ...
    def validate_order(self, symbol: str, action: str, size: float, price: float, context: dict = None) -> dict: ...
    def check_risk_limits(self, position: dict, context: dict = None) -> dict: ...
    def calculate_position_size(self, symbol: str, risk_level: float, portfolio_value: float, context: dict = None) -> float: ...
    def update_risk_metrics(self, trade_result: dict): ...
    def get_current_limits(self) -> dict: ...
    def reset(self): ...
    def save_snapshot(self, path: str = None): ...
```

---

## 3. Saídas e Retornos

| Método                    | Retorno | Descrição                                                          |
| ------------------------- | ------- | ------------------------------------------------------------------ |
| validate\_order           | dict    | Status e motivo da validação da ordem (aprovada/rejeitada, ajuste) |
| check\_risk\_limits       | dict    | Status/alerta dos limites para posição ativa                       |
| calculate\_position\_size | float   | Tamanho sugerido de posição para o risco desejado                  |
| update\_risk\_metrics     | None    | Atualiza métricas cumulativas de risco                             |
| get\_current\_limits      | dict    | Limites e métricas atuais (deep copy)                              |
| reset                     | None    | Limpa métricas acumuladas                                          |
| save\_snapshot            | None    | Salva snapshot de limites/métricas em CSV para auditoria           |

---

## 4. Fluxo de Execução

* validate\_order: rejeita ordem que exceda limites de risco, drawdown, exposição, SL/TP, com logs auditáveis.
* check\_risk\_limits: avalia limites ativos e emite alertas se necessário.
* calculate\_position\_size: sizing ideal conforme risco e SL, evitando sizing impossível.
* update\_risk\_metrics: atualiza cumulativos de drawdown, pnl, trades, wins, losses.
* get\_current\_limits: retorna snapshot (thread-safe) dos limites e métricas.
* reset: zera métricas acumuladas para novo ciclo.
* save\_snapshot: persiste snapshot para rastreio externo/auditoria (CSV).

---

## 5. Edge Cases e Validações

* Parâmetros faltantes ou inválidos: logs WARNING/ERROR, rejeita operação.
* Drawdown/exposição/risk excessivos: rejeição imediata, log detalhado.
* Falha ao carregar config: logs WARNING/ERROR, usa defaults seguros.
* Snapshot: cria diretório automaticamente, path curto para Windows.
* Thread safety via `threading.RLock()` (reentrante para evitar deadlock).

---

## 6. Integração e Compatibilidade

* Usa get\_logger, build\_filename, save\_dataframe do projeto.
* Plugável com TradeLogger, RewardAggregator, PositionManager, BaseEnv, TrainEnvLong/Short.
* Configurável por YAML/JSON (config\_path) ou por defaults.
* Testes usam tmp\_path do pytest; produção usa logs/audits/.

---

## 7. Docstring Google Style

```python
class RiskManager:
    """
    Gerencia limites de risco, sizing, SL/TP, drawdown e bloqueios em ambientes RL.

    Métodos principais:
      - validate_order: valida ordem conforme limites (risco, SL/TP, DD, exposição).
      - check_risk_limits: verifica limites ativos e emite alertas.
      - calculate_position_size: calcula tamanho ideal conforme risco/SL.
      - update_risk_metrics: atualiza métricas acumuladas.
      - get_current_limits: retorna snapshot atual.
      - reset: zera métricas de risco.
      - save_snapshot: salva snapshot de limites/métricas para auditoria.

    Args:
        config_path (str, opcional): Caminho da config YAML/JSON.
        logger (Logger, opcional): Logger estruturado.
        debug (bool): Ativa logs detalhados.
    """
    ...
```

---

## 8. Exemplo de Uso

```python
from src.env.env_libs.risk_manager import RiskManager
from src.utils.logging_utils import get_logger

logger = get_logger("RiskManager", debug=True)
rm = RiskManager(logger=logger)
result = rm.validate_order("EURUSD", "buy", 1.0, 1.105, context={"portfolio_value": 10000})
print(result)
size = rm.calculate_position_size("EURUSD", 0.01, 10000, context={"stop_loss": 50})
print(size)
rm.update_risk_metrics({"pnl": 10, "drawdown": 0.1})
snap = rm.get_current_limits()
print(snap)
rm.save_snapshot()
```

---

## 9. Testes e Validação

* Cobertura unitária dos métodos (validação, sizing, atualização, snapshot, reset, edge case)
* Testes usam tmp\_path do pytest, produção salva em logs/audits/
* Comando recomendado:

```bash
pytest tests/unit/test_risk_manager.py -v -s --log-cli-level=DEBUG
```

---

## 10. Checklist de Qualidade

* [x] Código PEP8, docstrings Google, imports absolutos
* [x] Logging detalhado, auditável e thread-safe (RLock)
* [x] Edge cases e rejeição segura (parâmetro, DD, SL/TP, snapshot)
* [x] Testes unitários e integração
* [x] Compatível com produção (logs/audits/) e testes (tmp\_path)

---

## 11. Rastreabilidade e Histórico

* DEVELOP\_TABLE.md: \[linha correspondente]
* REFERENCE\_TABLE.md: \[finalizar ciclo]
* DEV\_LOG.md: \[entrada do ciclo]
* TESTE: tests/unit/test\_risk\_manager.py
* SPEC\_TEMPLATE.md: v2.0
* Última atualização: 2025-06-08
* Autor: Equipe Op\_Trader

---

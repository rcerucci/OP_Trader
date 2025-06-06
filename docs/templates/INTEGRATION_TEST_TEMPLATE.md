# Template — Teste de Integração de Pipeline/Módulo

- **Arquivo:** `tests/integration/test_nome_modulo.py`

## 1. Objetivo

Descrever o objetivo da integração testada (ex: "Valida integração entre PositionManager, RiskManager e Logger no pipeline de execução do ambiente RL.")

## 2. Estrutura Recomendada

```python
import pytest
import os
from src.env.env_libs.execution.position_manager import PositionManager
from src.env.env_libs.risk.risk_manager import RiskManager
from src.utils.logging_utils import get_logger

@pytest.fixture
def setup_pipeline(tmp_path):
    # Inicializa dependências reais/mocks
    logger = get_logger("integration_test", debug=True, logs_dir=tmp_path)
    risk = RiskManager(config_path="config/environments/training.yaml", logger=logger)
    position = PositionManager(risk_manager=risk, logger=logger)
    return {"logger": logger, "risk": risk, "position": position}

def test_open_position_integration(setup_pipeline):
    """Valida ciclo completo de abertura de posição"""
    pm = setup_pipeline["position"]
    result = pm.manage_position(
        symbol="EURUSD",
        action="open",
        position_type="long",
        volume=0.1,
        stop_loss=1.08,
        take_profit=1.09
    )
    assert result["success"]
    # Valida propagação no risk manager
    assert pm.risk_manager.last_checked == "EURUSD"
    # Valida geração de log
    log_path = setup_pipeline["logger"].log_path
    with open(log_path, "r") as f:
        content = f.read()
        assert "Position opened" in content

def test_error_propagation_integration(setup_pipeline):
    """Valida erro e log de falha em fluxo de integração"""
    pm = setup_pipeline["position"]
    with pytest.raises(ValueError):
        pm.manage_position(
            symbol="INVALID",
            action="open",
            position_type="long",
            volume=0.1
        )
    # Confirma que erro foi logado
    log_path = setup_pipeline["logger"].log_path
    with open(log_path, "r") as f:
        content = f.read()
        assert "ERROR" in content
```

## 3. Checklist de Integração

- [ ] Usa fixtures ou dados reais/mocks adequados
- [ ] Valida interação entre pelo menos 2 módulos do pipeline
- [ ] Gera e verifica logs no padrão do projeto
- [ ] Salva outputs relevantes (CSV, logs) em `logs/` ou `outputs/`
- [ ] Testa tratamento de erro e propagação correta (exceções/logs)
- [ ] Documenta comportamento esperado para integração, edge cases e rollback

## ⚠️ Nota:

Este template é genérico e deve ser adaptado para cada pipeline/tipo de integração do projeto. Basta ajustar os módulos e funções de acordo com o fluxo principal do pipeline testado.
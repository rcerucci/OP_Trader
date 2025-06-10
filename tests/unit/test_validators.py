import pytest
from src.env.env_libs.validators import Validators

def test_validate_action_valid():
    assert Validators.validate_action("buy", ["buy", "sell"])
    assert Validators.validate_action("BUY", ["buy", "sell"])
    assert not Validators.validate_action("hold", ["buy", "sell"])

def test_validate_price():
    assert Validators.validate_price(1.1)
    assert not Validators.validate_price(-1)
    assert not Validators.validate_price(float('nan'))
    assert not Validators.validate_price(float('inf'))
    assert not Validators.validate_price(0)
    assert not Validators.validate_price(None)

def test_validate_size():
    assert Validators.validate_size(0.01)
    assert not Validators.validate_size(-1)
    assert not Validators.validate_size(0)
    assert not Validators.validate_size(float('nan'))

def test_validate_context():
    ctx = {"regime": "bull", "direction": "long"}
    assert Validators.validate_context(ctx, required_keys=["regime"])
    assert Validators.validate_context(ctx, required_keys=["regime", "direction"])
    assert not Validators.validate_context(ctx, required_keys=["missing"])
    assert Validators.validate_context(ctx, required_keys=[])
    assert Validators.validate_context(ctx)

def test_validate_schema():
    data = {"open": 1.0, "close": 1.1}
    schema = ["open", "close"]
    assert Validators.validate_schema(data, schema)
    with pytest.raises(ValueError):
        Validators.validate_schema(data, ["open", "close", "high"])
    with pytest.raises(ValueError):
        Validators.validate_schema(None, schema)

def test_validate_permissions():
    assert Validators.validate_permissions("user1", "admin", context={"role": "admin"})
    assert not Validators.validate_permissions("user2", "admin", context={"role": "trader"})
    assert Validators.validate_permissions("user2", "admin", context=None)

def test_log_validation(tmp_path):
    # Testa criação de logger e auditoria
    from src.utils.logging_utils import get_logger
    logger = get_logger("test_validators", cli_level="DEBUG")
    v = Validators(logger=logger)
    v.log_validation("price", True, "Preço validado com sucesso.")
    v.log_validation("action", False, "Ação não permitida.")
    # Apenas garantir que não lança erro; logs são verificados no console

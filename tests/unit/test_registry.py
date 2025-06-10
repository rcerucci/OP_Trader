import pytest
import logging
from src.env.registry import Registry

class DummyClass:
    pass

@pytest.fixture
def simple_logger():
    logger = logging.getLogger("SimpleTestLogger")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(message)s")
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    logger.propagate = True
    yield logger
    logger.handlers.clear()

@pytest.fixture
def registry_with_logger(simple_logger):
    return Registry(logger=simple_logger)

def test_register_and_get(registry_with_logger):
    reg = registry_with_logger
    reg.register("foo", DummyClass)
    assert reg.get("foo") == DummyClass

def test_register_duplicate_warns_and_overwrites(registry_with_logger, caplog):
    reg = registry_with_logger
    reg.register("dup", DummyClass)
    reg.register("dup", int)
    assert reg.get("dup") == int
    assert any("sobrescrevendo" in record.getMessage() for record in caplog.records)

def test_get_not_found_warns(registry_with_logger, caplog):
    reg = registry_with_logger
    reg.get("xpto")
    assert any("não registrado" in record.getMessage() for record in caplog.records)

def test_unregister_and_list(registry_with_logger, caplog):
    reg = registry_with_logger
    reg.register("foo", DummyClass)

    with caplog.at_level(logging.INFO, logger="SimpleTestLogger"):
        reg.unregister("foo")

    assert "removido do registro" in caplog.text.lower()

    assert reg.get("foo") is None



def test_list_and_type_filter(registry_with_logger):
    reg = registry_with_logger
    reg.register("cls1", DummyClass)
    reg.register("cls2", int)
    all_names = reg.list()
    assert set(all_names) == {"cls1", "cls2"}
    only_cls = reg.list(type_filter="Dummy")
    assert only_cls == ["cls1"]

def test_invalid_register_raises(registry_with_logger):
    reg = registry_with_logger
    with pytest.raises(ValueError):
        reg.register("", DummyClass)
    with pytest.raises(ValueError):
        reg.register("ok", None)

def test_reset_clears(registry_with_logger):
    reg = registry_with_logger
    reg.register("a", DummyClass)
    reg.reset()
    assert reg.list() == []

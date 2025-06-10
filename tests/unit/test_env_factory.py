import pytest
from src.env.env_factory import EnvFactory

# Mocks necessários
class DummyRegistry:
    def __init__(self):
        self._registry = {}

    def get(self, name):
        return self._registry.get(name)

    def register(self, name, cls):
        self._registry[name] = cls

class DummyEnv:
    def __init__(self, foo=None, bar=None, **kwargs):
        self.foo = foo
        self.bar = bar
        self.config = kwargs

class DummyWrapper:
    def __init__(self, env, **kwargs):
        self.env = env
        self.kwargs = kwargs

@pytest.fixture
def factory():
    registry = DummyRegistry()
    registry.register("dummy_env", DummyEnv)
    registry.register("dummy_wrapper", DummyWrapper)
    return EnvFactory(registry=registry, debug=True)

def test_register_and_list_envs_and_wrappers(factory):
    assert "dummy_env" in factory.registry._registry
    assert "dummy_wrapper" in factory.registry._registry

def test_create_env_basic(factory):
    env = factory.create_env("dummy_env", config_overrides={"foo": 123, "bar": "abc"})
    assert isinstance(env, DummyEnv)
    assert env.foo == 123
    assert env.bar == "abc"

def test_create_env_with_wrapper(factory):
    env = factory.create_env(
        "dummy_env",
        wrappers=[{"name": "dummy_wrapper", "params": {"param_test": True}}],
        config_overrides={"foo": 42}
    )
    assert hasattr(env, "env")  # wrapper aplicado
    assert hasattr(env.env, "foo")
    assert env.env.foo == 42
    assert env.kwargs["param_test"] is True

def test_create_env_env_not_registered():
    factory = EnvFactory(registry=DummyRegistry(), debug=True)
    with pytest.raises(ValueError):
        factory.create_env("nonexistent_env")

def test_create_env_wrapper_not_registered():
    registry = DummyRegistry()
    registry.register("dummy_env", DummyEnv)
    factory = EnvFactory(registry=registry, debug=True)
    with pytest.raises(ValueError):
        factory.create_env("dummy_env", wrappers=[{"name": "not_registered"}])

def test_registry_reset():
    registry = DummyRegistry()
    factory = EnvFactory(registry=registry, debug=True)
    factory.register_env("dummy_env", DummyEnv)
    factory.register_wrapper("dummy_wrapper", DummyWrapper)
    factory.reset_registry()
    assert factory.list_envs() == []
    assert factory.list_wrappers() == []

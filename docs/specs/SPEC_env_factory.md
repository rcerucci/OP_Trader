# SPEC\_env\_factory.md — src/env/env\_factory.py

---

## 1. Objetivo e Contexto

Módulo/fábrica central para criação, registro e orquestração de ambientes RL plugáveis do Op\_Trader. Permite injeção de wrappers, componentes, configuração dinâmica por arquivo (YAML/JSON) e gestão automatizada de pipelines PPO, supervisionados ou híbridos.

---

## 2. Entradas e Assinatura

| Parâmetro         | Tipo   | Obrigatório | Descrição                                   | Exemplo                    |
| ----------------- | ------ | ----------- | ------------------------------------------- | -------------------------- |
| config\_path      | str    | Não         | Caminho do arquivo de configuração global   | "configs/env\_config.yaml" |
| logger            | Logger | Não         | Logger estruturado                          | get\_logger("EnvFactory")  |
| debug             | bool   | Não         | Logging detalhado                           | True                       |
| env\_type         | str    | create\_env | Nome registrado do ambiente                 | "train\_env\_long"         |
| wrappers          | list   | create\_env | Lista de wrappers (nome ou classe/callable) | \["logging\_wrapper"]      |
| components        | dict   | create\_env | Instâncias plugáveis a serem injetadas      | {"risk\_manager": obj}     |
| config\_overrides | dict   | create\_env | Sobrescrita de parâmetros por ambiente      | {"foo": 123}               |

**Assinatura dos métodos:**

```python
class EnvFactory:
    def __init__(self, config_path: str = None, logger=None, debug: bool = False, **kwargs): ...
    def create_env(self, env_type: str, wrappers: list = None, components: dict = None, config_overrides: dict = None, **kwargs): ...
    def register_env(self, env_type: str, env_class): ...
    def register_wrapper(self, wrapper_name: str, wrapper_class): ...
    def list_envs(self) -> list: ...
    def list_wrappers(self) -> list: ...
    def reset_registry(self): ...
```

---

## 3. Saídas e Retornos

| Método            | Retorno | Descrição                                   |
| ----------------- | ------- | ------------------------------------------- |
| create\_env       | env     | Instância do ambiente configurado           |
| register\_env     | None    | Registra ambiente customizável              |
| register\_wrapper | None    | Registra wrapper customizável               |
| list\_envs        | list    | Lista os ambientes registrados              |
| list\_wrappers    | list    | Lista os wrappers registrados               |
| reset\_registry   | None    | Limpa todos os registros (ambiente/wrapper) |

---

## 4. Fluxo de Execução

* ****init**:** Inicializa registry, logger, carrega configs globais.
* **register\_env:** Registra ambiente plugável por nome/alias.
* **register\_wrapper:** Registra wrapper plugável por nome/alias.
* **create\_env:** Instancia ambiente, aplica wrappers, injeta componentes e configs.
* **list\_envs / list\_wrappers:** Consulta registry.
* **reset\_registry:** Limpa registry para hot-reload/testes.

---

## 5. Edge Cases e Validações

* Ambiente/wrapper não registrado: ValueError, log crítico
* Wrapper inválido: log crítico
* Falha ao carregar config: warning, fallback seguro
* Concorrência: thread-safe

---

## 6. Integração e Compatibilidade

* Compatível com todos ambientes RL Op\_Trader (TrainEnvLong, Short, Both, custom)
* Permite registro de wrappers como LoggingWrapper, NormalizationWrapper, etc
* Carrega configuração global (YAML/JSON), sobrescrita via parâmetro
* Compatível com pytest, pipelines multi-ambiente, produção

---

## 7. Docstring Google Style

```python
class EnvFactory:
    """
    Fábrica central de ambientes RL plugáveis para Op_Trader.

    Métodos principais:
      - register_env/register_wrapper: registro plugável.
      - create_env: instancia, injeta componentes, aplica wrappers.
      - list_envs/list_wrappers: consulta.
      - reset_registry: hot-reload/testes.

    Args:
        config_path (str, opcional): Caminho configuração.
        logger (Logger, opcional): Logger estruturado.
        debug (bool): Logging detalhado.
    """
    ...
```

---

## 8. Exemplo de Uso

```python
from src.env.env_factory import EnvFactory
from src.env.environments.train_env_long import TrainEnvLong
from src.env.wrappers.logging_wrapper import LoggingWrapper

factory = EnvFactory()
factory.register_env("train_env_long", TrainEnvLong)
factory.register_wrapper("logging_wrapper", LoggingWrapper)

env = factory.create_env(
    "train_env_long",
    wrappers=["logging_wrapper"],
    config_overrides={"context_macro": {"direction": "long"}, "debug": True}
)
obs, info = env.reset()
```

---

## 9. Testes e Validação

* Cobertura unitária dos métodos (registro, criação, wrappers, config, reset, erro)
* Testes recomendados:

```bash
pytest tests/unit/test_env_factory.py -v -s --log-cli-level=DEBUG
```

* Homologação inclui: registro, criação, wrappers, componentes, erro, reset, logging

---

## 10. Checklist de Qualidade

* [x] Docstrings Google Style, código PEP8
* [x] Logging detalhado, rastreável
* [x] Edge cases (não registrado, config, reset, wrapper inválido)
* [x] Testes unitários e integração
* [x] Compatível com pipelines RL e produção
* [x] Exemplo validado e testado

---

## 11. Rastreabilidade e Histórico

* DEVELOP\_TABLE.md: linha EnvFactory, src/env/env\_factory.py, @CODE (marcar @STABLE ao final do ciclo environments)
* REFERENCE\_TABLE.md: a ser movido após o ciclo completo
* DEV\_LOG.md: ciclo 2025-06-08 homologado, todos os testes unitários e integração passaram
* TESTE: tests/unit/test\_env\_factory.py
* SPEC\_TEMPLATE.md: v2.0
* Última atualização: 2025-06-08
* Autor: Equipe Op\_Trader

---

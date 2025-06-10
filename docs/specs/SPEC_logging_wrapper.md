# SPEC\_registry.md

---

## 1. Objetivo e Contexto

O módulo **Registry** é responsável por manter um registro centralizado, thread-safe e auditável dos ambientes, wrappers e outros componentes do Op\_Trader. Ele permite registrar, buscar, remover, listar e resetar componentes pelo nome, garantindo controle e rastreabilidade via logging estruturado.

Esse registro é fundamental para o gerenciamento dinâmico dos componentes do sistema durante o desenvolvimento, testes e produção, facilitando a manutenção e extensão do pipeline RL.

---

## 2. Entradas e Assinatura

| Parâmetro | Tipo   | Obrigatório | Descrição                                     | Exemplo                  |
| --------- | ------ | ----------- | --------------------------------------------- | ------------------------ |
| logger    | Logger | Não         | Logger estruturado para registros e auditoria | `get_logger("Registry")` |
| debug     | bool   | Não         | Habilita logs de debug detalhados             | `True`                   |

### Métodos principais

```python
class Registry:
    def __init__(self, logger: Optional[Any] = None, debug: bool = False): ...
    def register(self, name: str, obj: Any): ...
    def get(self, name: str) -> Any: ...
    def unregister(self, name: str): ...
    def list(self, type_filter: Optional[str] = None) -> List[str]: ...
    def reset(self): ...
```

---

## 3. Saídas e Retornos

| Método     | Retorno     | Descrição                                         |
| ---------- | ----------- | ------------------------------------------------- |
| register   | None        | Registra o objeto no registro                     |
| get        | Any ou None | Retorna o objeto registrado ou None               |
| unregister | None        | Remove o objeto do registro                       |
| list       | List\[str]  | Lista nomes registrados, podendo filtrar por tipo |
| reset      | None        | Limpa todo o registro                             |

---

## 4. Fluxo de Execução

* `__init__`: Inicializa o registro, lock para thread safety e logger.
* `register`: Valida parâmetros, registra objeto, loga operação, alerta sobre sobrescrita.
* `get`: Busca objeto por nome, loga sucesso ou aviso se não encontrado.
* `unregister`: Remove objeto, loga sucesso ou aviso/erro para condições especiais.
* `list`: Retorna lista de nomes, aplica filtro opcional por nome da classe.
* `reset`: Limpa o registro, loga operação.

---

## 5. Edge Cases e Validações

* Registro com nome inválido ou objeto None gera `ValueError`.
* Registro sobrescrevendo objeto existente gera log de `WARNING`.
* Busca de nome não registrado gera log de `WARNING` e retorna None.
* Remoção de nome não registrado gera log de `WARNING`.
* Remoção de nomes críticos (ex: "env\_factory") gera log `CRITICAL`.
* Filtro de listagem considera case insensitive no nome da classe.
* Proteção contra concorrência via `threading.RLock`.

---

## 6. Integração e Compatibilidade

* Compatível com pipelines Op\_Trader e seus módulos RL.
* Integra com sistema de logging oficial do projeto (`get_logger`).
* Preparado para ser usado em testes unitários, integração e produção.
* Compatível com o padrão Pytest e captura de logs via `caplog`.

---

## 7. Docstrings Google Style

```python
class Registry:
    """
    Registro dinâmico e thread-safe para componentes RL do Op_Trader.

    Args:
        logger (Logger, opcional): Logger estruturado.
        debug (bool): Habilita logs de debug.

    Métodos:
        - register: Registra componente.
        - get: Busca componente.
        - unregister: Remove componente.
        - list: Lista componentes.
        - reset: Limpa registro.

    Raises:
        ValueError: Para parâmetros inválidos.

    Example:
        >>> reg = Registry()
        >>> reg.register("train_env_long", TrainEnvLong)
        >>> env_cls = reg.get("train_env_long")
        >>> reg.unregister("train_env_long")
        >>> reg.reset()
    """
```

---

## 8. Exemplo de Uso

```python
from src.env.registry import Registry
from src.env.environments.train_env_long import TrainEnvLong

reg = Registry()
reg.register("train_env_long", TrainEnvLong)

env_cls = reg.get("train_env_long")
print(env_cls)  # <class 'TrainEnvLong'>

reg.unregister("train_env_long")

reg.reset()
```

---

## 9. Testes e Validação

Testes unitários garantem:

* Registro e busca corretos.
* Sobrescrita de registro gera aviso.
* Busca de nome inexistente gera aviso.
* Remoção e reset funcionam corretamente.
* Filtro de listagem por tipo funciona.
* Validações de erros para entradas inválidas.

---

## 10. Checklist de Qualidade

* [x] Docstrings Google Style
* [x] Logging detalhado e rastreável
* [x] Testes unitários e integração completos
* [x] Proteção thread-safe com `RLock`
* [x] Compatibilidade com Pytest e caplog
* [x] Exemplo prático validado
* [x] Alinhamento total com padrões Op\_Trader

---

## 11. Rastreabilidade e Histórico

* Arquivo: `src/env/registry.py`
* Testes: `tests/unit/test_registry.py`
* Última atualização: 2025-06-08
* Responsável: Equipe Op\_Trader
* Status: @STABLE homologado

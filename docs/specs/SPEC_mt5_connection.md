# mt5\_connection — Especificação Técnica (SPEC.md)

## Docstring Padrão do Projeto

```python
"""
src/utils/mt5_connection.py
Módulo utilitário para conectar e desconectar do MetaTrader5 usando variáveis .env, logging padronizado e controle robusto de exceções para o pipeline Op_Trader.
Autor: Equipe Op_Trader
Data: 2025-06-06
"""
```

---

## 1. Objetivo

Facilitar integração segura e auditável entre o Op\_Trader e o MetaTrader5, centralizando lógica de conexão, shutdown, logging e controle de variáveis de ambiente.

**Funcionalidades principais:**

* Conectar ao MT5 usando variáveis .env
* Logging informativo em todas as etapas
* Raise e logging explícitos para variáveis ausentes e falhas de conexão
* Encerrar conexão de forma segura

---

## 2. Entradas

| Parâmetro  | Tipo     | Obrigatório | Descrição               | Exemplo |
| ---------- | -------- | ----------- | ----------------------- | ------- |
| cli\_level | str, opc | Não         | Nível de log CLI/config | "DEBUG" |

---

## 3. Saídas

| Função                 | Tipo Retorno | Descrição                                | Exemplo                  |
| ---------------------- | ------------ | ---------------------------------------- | ------------------------ |
| connect\_to\_mt5       | bool         | True se conexão ok, False/raise se falha | ok = connect\_to\_mt5()  |
| close\_mt5\_connection | None         | Encerra conexão e gera log               | close\_mt5\_connection() |

---

## 4. Exceções e Validações

| Caso                           | Exceção/Retorno | Descrição                     |
| ------------------------------ | --------------- | ----------------------------- |
| Variáveis de ambiente ausentes | RuntimeError    | Falta login/senha/server .env |
| Falha ao inicializar mt5       | False           | Loga erro e retorna False     |
| Falha ao encerrar conexão      | RuntimeError    | Loga erro e raise             |

---

## 5. Docstring Padrão (Google Style)

```python
def connect_to_mt5(cli_level: Optional[str] = None) -> bool:
    """
    Inicializa conexão com MetaTrader5, logando cada etapa.
    Carrega credenciais do .env localizado na raiz do projeto.

    Args:
        cli_level (Optional[str]): Nível de log ('DEBUG', 'INFO', etc).
    Returns:
        bool: True se conexão bem sucedida, False caso contrário.
    Raises:
        RuntimeError: Se variáveis obrigatórias não forem encontradas.
    Example:
        >>> ok = connect_to_mt5(cli_level='DEBUG')
    """
```

---

## 6. Exemplo de Uso

```python
from src.utils.mt5_connection import connect_to_mt5, close_mt5_connection
ok = connect_to_mt5(cli_level='DEBUG')
if not ok:
    raise RuntimeError("Falha ao conectar ao MT5")
close_mt5_connection()
```

---

## 7. Regras de Negócio e Observações

* Sempre ler as variáveis MT5\_LOGIN, MT5\_PASSWORD e MT5\_SERVER do .env
* Raise explícito para variáveis ausentes
* Logging obrigatório para todas as etapas e falhas
* Retorno False em erro de conexão, raise em shutdown mal sucedido
* Nunca armazena credenciais sensíveis em logs

---

## 8. Edge Cases

* .env ausente ou variáveis não setadas: raise RuntimeError
* mt5.initialize retorna False: loga erro com código/mensagem
* Falha no shutdown: raise RuntimeError e loga

---

## 9. Dependências

**Depende de:**

* `os`, `sys`, `MetaTrader5`, `dotenv`, `pathlib`
* `src.utils.logging_utils.get_logger`
* `src.utils.path_setup.ensure_project_root`

**Não deve depender de:**

* Módulos/modelos internos do pipeline, lógica de trading

---

## 10. Checklist de Qualidade (conforme CONTRIBUTING.md)

* [x] Docstrings Google Style e exemplos
* [x] Logging detalhado e raise explícito para erros
* [x] Imports absolutos
* [x] Exemplo prático
* [x] Edge cases cobertos

---

## 11. Histórico

| Data       | Autor             | Alteração                      |
| ---------- | ----------------- | ------------------------------ |
| 2025-06-06 | Equipe Op\_Trader | Criação inicial e padronização |

---

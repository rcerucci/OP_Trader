# logging\_utils — Especificação Técnica (SPEC.md)

## Docstring Padrão do Projeto

```python
"""
src/utils/logging_utils.py
Camada central de logging do Op_Trader, criando loggers padronizados, coloridos, auditáveis e compatíveis com ambientes variados (CLI, scripts, testes, notebooks).
Autor: Equipe Op_Trader
Data: 2025-06-06
"""
```

---

## 1. Objetivo

Este módulo fornece funções utilitárias para criação e configuração de loggers em toda a base de código do Op\_Trader.
Permite controle granular do nível de log via config.ini ou CLI, saída colorida quando possível e impede duplicação de handlers em ambientes interativos.

**Funcionalidades principais:**

* `get_logger`: logger padronizado para qualquer módulo
* Carrega nível de log do config.ini ou CLI
* Suporte a colorlog se disponível
* Remove handlers antigos para evitar logs duplicados
* Integração fácil com tqdm e ambientes diversos

---

## 2. Entradas

| Parâmetro  | Tipo               | Obrigatório | Descrição                                         | Exemplo             |
| ---------- | ------------------ | ----------- | ------------------------------------------------- | ------------------- |
| name       | str                | Sim         | Nome do logger (geralmente **name**)              | "src.data.pipeline" |
| cli\_level | int \| str \| None | Não         | Nível de log (CLI ou config). Default: config.ini | "DEBUG"             |

---

## 3. Saídas

| Nome   | Tipo           | Descrição                            | Exemplo                 |
| ------ | -------------- | ------------------------------------ | ----------------------- |
| logger | logging.Logger | Logger configurado e pronto para uso | logger.info("Mensagem") |

---

## 4. Exceções e Validações

| Caso                            | Exceção/Retorno | Descrição                          |
| ------------------------------- | --------------- | ---------------------------------- |
| name vazio ou inválido          | ValueError      | Nome do logger não pode ser vazio  |
| colorlog ausente                | -               | Fallback para StreamHandler padrão |
| config.ini inválido/inexistente | -               | Usa nível WARNING por padrão       |

---

## 5. Docstring Padrão (Google Style)

```python
def get_logger(name: str, cli_level: Optional[Union[int, str]] = None) -> logging.Logger:
    """
    Obtém um logger padronizado do projeto Op_Trader.

    Args:
        name (str): Nome do logger, geralmente __name__.
        cli_level (int | str | None): Nível passado via CLI ou código. "DEBUG", "INFO", int do logging, ou None.

    Returns:
        logging.Logger: Logger configurado, pronto para uso.

    Example:
        >>> log = get_logger("pipeline", cli_level="DEBUG")
        >>> log.info("Processo iniciado")
    """
```

---

## 6. Exemplo de Uso

```python
from src.utils.logging_utils import get_logger
logger = get_logger(__name__, cli_level="INFO")
logger.info("Mensagem testada com padrão Op_Trader")
```

---

## 7. Regras de Negócio e Observações

* Níveis aceitos: NONE, ERROR, WARNING, INFO, DEBUG
* Sempre remove handlers antigos para evitar logs duplicados
* Fallback automático para console simples se colorlog ausente
* Em ambientes CLI/scripts/notebooks: funcionamento garantido
* Integração recomendada com tqdm usando tqdm.write() para evitar quebra de barras

---

## 8. Edge Cases

* colorlog não instalado: fallback silencioso
* Múltiplos loggers para o mesmo nome: remove e substitui handler
* config.ini ausente/inválido: default WARNING
* Uso em notebooks/scripts/tests: nunca duplica handler

---

## 9. Dependências

**Depende de:**

* `logging` (stdlib), `colorlog` (opcional)
* `configparser`, `pathlib.Path`
* `src.utils.path_setup.ensure_project_root`

**Não deve depender de:**

* Qualquer recurso externo ao logging/config padrão do projeto

---

## 10. Checklist de Qualidade (conforme CONTRIBUTING.md)

* [x] Docstrings padrão Google e exemplos
* [x] Interface robusta (fallback colorlog, default WARNING)
* [x] Imports absolutos
* [x] Não duplica handlers
* [x] Testes funcionais indiretos (pipeline, scripts)

---

## 11. Histórico

| Data       | Autor             | Alteração                      |
| ---------- | ----------------- | ------------------------------ |
| 2025-06-06 | Equipe Op\_Trader | Criação inicial e padronização |

---

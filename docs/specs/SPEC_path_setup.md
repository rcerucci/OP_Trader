# path\_setup — Especificação Técnica (SPEC.md)

## Docstring Padrão do Projeto

```python
"""
src/utils/path_setup.py
Função utilitária para garantir que a raiz do projeto esteja no sys.path e permitir imports absolutos na estrutura Op_Trader.
Autor: Equipe Op_Trader
Data: 2025-06-06
"""
```

---

## 1. Objetivo

Este módulo provê a função utilitária `ensure_project_root`, fundamental para permitir que qualquer script do projeto, independentemente do diretório de execução, consiga importar módulos de forma absoluta a partir da raiz (`src/`). Garante portabilidade e padronização do ambiente Python no Op\_Trader.

**Funcionalidades principais:**

* Adicionar a raiz do projeto ao `sys.path` se necessário
* Permitir imports absolutos em toda a base de código
* Retornar o objeto Path da raiz do projeto
* Logging informativo quando possível (opcional, tolerante a ausência do módulo de logging)

---

## 2. Entradas

| Parâmetro | Tipo        | Obrigatório | Descrição                                            | Exemplo    |
| --------- | ----------- | ----------- | ---------------------------------------------------- | ---------- |
| cur\_file | str \| Path | Sim         | Caminho do arquivo corrente (normalmente `__file__`) | `__file__` |

---

## 3. Saídas

| Nome | Tipo | Descrição                                    | Exemplo                |
| ---- | ---- | -------------------------------------------- | ---------------------- |
| root | Path | Objeto Path apontando para a raiz do projeto | `/home/user/op_trader` |

---

## 4. Exceções e Validações

| Caso                         | Exceção/Retorno | Descrição                                                       |
| ---------------------------- | --------------- | --------------------------------------------------------------- |
| Caminho inválido/muito curto | ValueError      | Não foi possível resolver a raiz do projeto para o arquivo dado |

---

## 5. Docstring Padrão (Google Style)

```python
def ensure_project_root(cur_file: Union[str, Path]) -> Path:
    """
    Garante que a raiz do projeto esteja no sys.path para permitir imports absolutos.

    Args:
        cur_file (str | Path): Caminho do arquivo atual (__file__).

    Returns:
        Path: Objeto Path apontando para a raiz do projeto.

    Raises:
        ValueError: Se não for possível resolver o caminho esperado da raiz.

    Example:
        >>> from src.utils.path_setup import ensure_project_root
        >>> ROOT_DIR = ensure_project_root(__file__)
    """
```

---

## 6. Exemplo de Uso

```python
from src.utils.path_setup import ensure_project_root
ROOT_DIR = ensure_project_root(__file__)
```

---

## 7. Regras de Negócio e Observações

* A raiz do projeto é sempre considerada 2 níveis acima do arquivo do módulo (`src/utils/…`)
* Logging de debug é gerado se logging\_utils estiver disponível, mas nunca gera erro se não estiver
* Função é idempotente: múltiplas chamadas não causam duplicação no sys.path
* Caso o diretório não possa ser resolvido corretamente, levanta ValueError

---

## 8. Edge Cases

* Caminho de arquivo inválido ou muito curto: raise ValueError
* sys.path já contém a raiz: operação é silenciosa
* logging\_utils não disponível: não trava execução

---

## 9. Dependências

**Depende de:**

* `sys`, `pathlib.Path` (stdlib)
* (Opcional, tolerante) `src.utils.logging_utils.get_logger`

**Não deve depender de:**

* Nenhum recurso externo ao Python padrão
* Qualquer módulo de negócio do projeto

---

## 10. Checklist de Qualidade (conforme CONTRIBUTING.md)

* [x] Docstring padrão Google
* [x] Logging opcional
* [x] Imports absolutos
* [x] Raise explícito para erros
* [x] Exemplo de uso na docstring
* [x] Testes indiretos via outros módulos

---

## 11. Histórico

| Data       | Autor             | Alteração                      |
| ---------- | ----------------- | ------------------------------ |
| 2025-06-06 | Equipe Op\_Trader | Criação inicial e padronização |

---
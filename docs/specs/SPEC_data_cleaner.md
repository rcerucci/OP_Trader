# data\_cleaner — Especificação Técnica (SPEC.md)

## Docstring Padrão do Projeto

```python
"""
src/utils/data_cleaner.py
Classe utilitária para limpeza e padronização de DataFrames de candles no pipeline Op_Trader.
Autor: Equipe Op_Trader
Data: 2025-06-06
"""
```

---

## 1. Objetivo

Padronizar e validar DataFrames de candles lidos de fontes externas, garantindo compatibilidade com o pipeline do Op\_Trader para feature engineering.

**Funcionalidades principais:**

* Padroniza nomes de colunas (“date”→“time”, “volume”→“tick\_volume”)
* Valida presença das colunas obrigatórias
* Converte tipos (“time” para datetime, valores para float64)
* Remove linhas inválidas (NaN)
* Ordena por timestamp
* Logging detalhado e robusto

---

## 2. Entradas

| Parâmetro | Tipo         | Obrigatório | Descrição                          | Exemplo    |
| --------- | ------------ | ----------- | ---------------------------------- | ---------- |
| df        | pd.DataFrame | Sim         | DataFrame bruto de candles         | df\_raw    |
| debug     | bool         | Não         | Ativa logs detalhados na instância | True/False |

---

## 3. Saídas

| Nome | Tipo         | Descrição                     | Exemplo   |
| ---- | ------------ | ----------------------------- | --------- |
| df   | pd.DataFrame | DataFrame limpo e padronizado | df\_clean |

---

## 4. Exceções e Validações

| Caso                       | Exceção/Retorno | Descrição                               |
| -------------------------- | --------------- | --------------------------------------- |
| df vazio                   | ValueError      | Não processa DataFrames vazios          |
| Coluna obrigatória ausente | KeyError        | Falta campo essencial após renomeações  |
| Falha ao converter dtype   | ValueError      | Coluna de valor não pôde ser convertida |

---

## 5. Docstring Padrão (Google Style)

```python
class DataCleaner:
    """
    Limpa e padroniza DataFrames de candles para o pipeline Op_Trader.

    Métodos:
        - clean(df): Limpa, valida e retorna DataFrame pronto para feature engineering.

    Args:
        debug (bool): Se True, logging detalhado.
    """

    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Realiza a limpeza e padronização do DataFrame.

        Args:
            df (pd.DataFrame): DataFrame bruto lido do CSV.
        Returns:
            pd.DataFrame: DataFrame limpo e padronizado.
        Raises:
            KeyError: Se faltar coluna obrigatória.
            ValueError: Se DataFrame de entrada estiver vazio ou com tipos inválidos.
        Example:
            >>> cleaner = DataCleaner(debug=True)
            >>> df_clean = cleaner.clean(df_raw)
        """
```

---

## 6. Exemplo de Uso

```python
from src.utils.data_cleaner import DataCleaner
cleaner = DataCleaner(debug=True)
df_clean = cleaner.clean(df_raw)
```

---

## 7. Regras de Negócio e Observações

* Sempre converte/renomeia para os nomes e tipos padrão do projeto
* DataFrames vazios nunca devem ser processados
* Toda exceção é logada antes de ser lançada
* Ao final, shape e integridade do DataFrame são auditáveis pelo log

---

## 8. Edge Cases

* DataFrame vazio: raise ValueError
* Colunas obrigatórias ausentes: raise KeyError
* Coluna com dados não conversíveis: raise ValueError
* Linhas com time inválido: convertidas para NaT e removidas no dropna

---

## 9. Dependências

**Depende de:**

* `pandas`
* `src.utils.logging_utils.get_logger`
* `src.utils.path_setup.ensure_project_root`

**Não deve depender de:**

* Módulos de negócio ou lógica específica de trading/modelagem

---

## 10. Checklist de Qualidade (conforme CONTRIBUTING.md)

* [x] Docstrings Google Style e exemplos
* [x] Logging detalhado em cada etapa crítica
* [x] Raise explícito para casos inválidos
* [x] Imports absolutos
* [x] Exemplo de uso prático
* [x] Edge cases auditados

---

## 11. Histórico

| Data       | Autor             | Alteração                      |
| ---------- | ----------------- | ------------------------------ |
| 2025-06-06 | Equipe Op\_Trader | Criação inicial e padronização |

---

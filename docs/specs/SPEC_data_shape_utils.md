# data\_shape\_utils — Especificação Técnica (SPEC.md)

## Docstring Padrão do Projeto

```python
"""
src/utils/data_shape_utils.py
Funções utilitárias para alinhamento e validação de DataFrames de features ao schema esperado pelo pipeline Op_Trader.
Autor: Equipe Op_Trader
Data: 2025-06-06
"""
```

---

## 1. Objetivo

Fornecer funções utilitárias para carregar lista de features a partir dos arquivos de schema e garantir que DataFrames estejam alinhados ao formato esperado, tanto em ordem de colunas quanto em tipos (float64).

**Funcionalidades principais:**

* `load_feature_list`: carrega lista "all\_features" do schema ativo
* `align_dataframe_to_schema`: força DataFrame a seguir exatamente o schema de colunas e tipos

---

## 2. Entradas

| Parâmetro            | Tipo                        | Obrigatório | Descrição                                                  | Exemplo      |
| -------------------- | --------------------------- | ----------- | ---------------------------------------------------------- | ------------ |
| df (align)           | pd.DataFrame                | Sim         | DataFrame de entrada                                       | df\_features |
| schema\_cols (align) | list\[str], tuple\[str,...] | Sim         | Lista/tupla de colunas do schema desejado                  | features     |
| - (load)             | -                           | -           | Usa config/control via JSON (não recebe argumento externo) | -            |

---

## 3. Saídas

| Função                       | Tipo Retorno | Descrição                                            | Exemplo                        |
| ---------------------------- | ------------ | ---------------------------------------------------- | ------------------------------ |
| load\_feature\_list          | list\[str]   | Lista de nomes de features do schema ativo           | \['close','rsi','ema\_20',...] |
| align\_dataframe\_to\_schema | pd.DataFrame | DataFrame alinhado ao schema (ordem e dtype float64) | aligned\_df                    |

---

## 4. Exceções e Validações

| Caso                                   | Exceção/Retorno            | Descrição                                    |
| -------------------------------------- | -------------------------- | -------------------------------------------- |
| feature\_schema.json ausente/inválido  | FileNotFoundError/KeyError | Arquivo ou campo esperado ausente            |
| Arquivo de schema referenciado ausente | FileNotFoundError          | Idem                                         |
| Campo 'all\_features' ausente/vazio    | Warning logado             | Não impede execução, mas alerta via logger   |
| df não é DataFrame (align)             | TypeError                  | align\_dataframe\_to\_schema exige DataFrame |

---

## 5. Docstring Padrão (Google Style)

```python
def align_dataframe_to_schema(df: pd.DataFrame, schema_cols: Sequence[str]) -> pd.DataFrame:
    """
    Alinha o DataFrame às colunas do schema, preservando ordem e tipos.
    Preenche colunas ausentes com np.nan, garante dtype float64.

    Args:
        df (pd.DataFrame): DataFrame de entrada.
        schema_cols (Sequence[str]): Lista ou tupla de colunas do schema.
    Returns:
        pd.DataFrame: DataFrame alinhado ao schema.
    Raises:
        TypeError: Se df não for DataFrame.
    Example:
        >>> aligned = align_dataframe_to_schema(df, features)
    """
```

---

## 6. Exemplo de Uso

```python
from src.utils.data_shape_utils import load_feature_list, align_dataframe_to_schema
features = load_feature_list()
aligned = align_dataframe_to_schema(df, features)
```

---

## 7. Regras de Negócio e Observações

* Todo pipeline de features deve usar lista obtida por load\_feature\_list
* DataFrame de entrada pode conter colunas extras, mas só as do schema serão mantidas
* Colunas ausentes são criadas e preenchidas com np.nan
* Tipos sempre convertidos para float64, loga se houver conversão
* Ordens de colunas SEMPRE igual ao schema

---

## 8. Edge Cases

* Arquivos de controle/schema ausentes: erro explícito
* df sem índice ou colunas: output vazio, mas com colunas do schema
* all\_features vazio: warning no logger

---

## 9. Dependências

**Depende de:**

* `json`, `pandas`, `numpy`
* `src.utils.logging_utils.get_logger`
* `src.utils.path_setup.ensure_project_root`

**Não deve depender de:**

* Qualquer módulo de negócio ou função específica de treinamento/modelagem

---

## 10. Checklist de Qualidade (conforme CONTRIBUTING.md)

* [x] Docstrings Google Style
* [x] Logging em todas operações críticas
* [x] Raise explícito para erros de arquivo/campo
* [x] Imports absolutos
* [x] Exemplo de uso prático
* [x] Edge cases documentados

---

## 11. Histórico

| Data       | Autor             | Alteração                      |
| ---------- | ----------------- | ------------------------------ |
| 2025-06-06 | Equipe Op\_Trader | Criação inicial e padronização |

---

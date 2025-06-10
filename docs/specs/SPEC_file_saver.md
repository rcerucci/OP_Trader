# file\_saver — Especificação Técnica (SPEC.md)

## Docstring Padrão do Projeto

```python
"""
src/utils/file_saver.py
Utilitários para geração de nomes de arquivos com timestamp e salvamento seguro de DataFrames, compatíveis com a convenção de auditoria do Op_Trader.
Autor: Equipe Op_Trader
Data: 2025-06-06
"""
```

---

## 1. Objetivo

Fornecer funções utilitárias para geração padronizada de nomes de arquivos e salvamento seguro de DataFrames (CSV), garantindo criação de diretórios e logs, conforme a convenção do Op\_Trader para rastreabilidade de dados e modelos.

**Funcionalidades principais:**

* `get_timestamp`: gera timestamp padrão para arquivos
* `build_filename`: constrói nome de arquivo padronizado (prefix, sufixo, ativo, timeframe, período, timestamp, extensão)
* `save_dataframe`: salva DataFrame como CSV, criando diretórios e auditando

---

## 2. Entradas

| Parâmetro       | Tipo          | Obrigatório | Descrição                                        | Exemplo                  |
| --------------- | ------------- | ----------- | ------------------------------------------------ | ------------------------ |
| prefix          | str           | Sim         | Diretório base (ex: "data/processed")            | "data/processed"         |
| suffix          | str           | Sim         | Prefixo do arquivo (ex: "features")              | "features"               |
| asset           | str           | Sim         | Símbolo do ativo (ex: "EURUSD")                  | "EURUSD"                 |
| timeframe       | str           | Sim         | Timeframe do ativo (ex: "M5")                    | "M5"                     |
| period          | str, opcional | Não         | String de período (ex: "2024-01-01\_2024-12-31") | "2024-01-01\_2024-12-31" |
| timestamp       | str, opcional | Não         | Timestamp (ex: get\_timestamp())                 | "20250606\_213154"       |
| extension       | str, opcional | Não         | Extensão do arquivo (default: "csv")             | "csv"                    |
| df (save)       | pd.DataFrame  | Sim         | DataFrame a ser salvo                            | -                        |
| filepath (save) | str           | Sim         | Caminho completo de saída para salvar arquivo    | "data/processed/feat..." |

---

## 3. Saídas

| Função          | Tipo Retorno | Descrição                                | Exemplo                     |
| --------------- | ------------ | ---------------------------------------- | --------------------------- |
| get\_timestamp  | str          | Timestamp YYYYMMDD\_HHMMSS               | "20250606\_213154"          |
| build\_filename | str          | Caminho completo do arquivo              | "data/processed/feat...csv" |
| save\_dataframe | None         | Salva arquivo, gera log ou raise em erro | -                           |

---

## 4. Exceções e Validações

| Caso                          | Exceção/Retorno | Descrição                                              |
| ----------------------------- | --------------- | ------------------------------------------------------ |
| Parâmetro obrigatório ausente | ValueError      | build\_filename exige prefix, suffix, asset, timeframe |
| Falha ao criar diretório      | OSError         | save\_dataframe raise em erro de permissão/diretório   |
| Falha ao salvar arquivo       | IOError         | save\_dataframe raise e loga erro ao salvar CSV        |

---

## 5. Docstring Padrão (Google Style)

```python
def build_filename(prefix: str, suffix: str, asset: str, timeframe: str, period: Optional[str] = "", timestamp: Optional[str] = "", extension: str = "csv") -> str:
    """
    Gera nome de arquivo padronizado do projeto, com sufixos opcionais.

    Args:
        prefix (str): Diretório base.
        suffix (str): Prefixo do arquivo.
        asset (str): Símbolo do ativo.
        timeframe (str): Timeframe.
        period (str, optional): String de período.
        timestamp (str, optional): Timestamp.
        extension (str, optional): Extensão do arquivo.
    Returns:
        str: Caminho completo do arquivo.
    Raises:
        ValueError: Se campos obrigatórios estiverem vazios.
    Example:
        >>> build_filename("data/raw", "market", "EURUSD", "M5", "2024-01-01_2024-12-31", "20250606_213154")
        'data/raw/market_EURUSD_M5_2024-01-01_2024-12-31_20250606_213154.csv'
    """
```

---

## 6. Exemplo de Uso

```python
from src.utils.file_saver import get_timestamp, build_filename, save_dataframe
ts = get_timestamp()
fname = build_filename("data/processed", "features", "EURUSD", "M5", "2024-01-01_2024-12-31", ts)
save_dataframe(df, fname)
```

---

## 7. Regras de Negócio e Observações

* Nomenclatura padrão deve ser seguida em todo pipeline
* Logging detalhado é obrigatório ao salvar arquivos
* Diretórios devem ser criados automaticamente se não existirem
* Não sobrescreve arquivos existentes sem aviso prévio (por padrão, CSV do pandas sobrescreve; revisão futura pode adicionar opção safe)

---

## 8. Edge Cases

* Parâmetro obrigatório vazio em build\_filename: raise explícito
* Diretório de destino sem permissão: raise OSError em save\_dataframe
* Falha de escrita (disco cheio, permissão): raise IOError
* Caminho já existente: sobrescreve (com log)

---

## 9. Dependências

**Depende de:**

* `os`, `datetime`, `pandas`
* `src.utils.logging_utils.get_logger`
* `src.utils.path_setup.ensure_project_root`

**Não deve depender de:**

* Módulos de negócio ou lógica de pipeline de dados

---

## 10. Checklist de Qualidade (conforme CONTRIBUTING.md)

* [x] Docstrings Google Style em todas funções
* [x] Logging em operações críticas
* [x] Raise explícito para campos obrigatórios
* [x] Imports absolutos
* [x] Exemplo prático
* [x] Cobertura de edge cases via raise

---

## 11. Histórico

| Data       | Autor             | Alteração                      |
| ---------- | ----------------- | ------------------------------ |
| 2025-06-06 | Equipe Op\_Trader | Criação inicial e padronização |

---

# scaler\_utils — Especificação Técnica (SPEC.md)

## Docstring Padrão do Projeto

```python
"""
src/utils/scaler_utils.py
Classe utilitária para ajuste, aplicação e persistência de StandardScaler (scikit-learn) para features contínuas do Op_Trader.
Autor: Equipe Op_Trader
Data: 2025-06-06
"""
```

---

## 1. Objetivo

Permitir normalização consistente de features contínuas do pipeline via StandardScaler, garantindo auditabilidade (salvar/carregar) e logging robusto em todas as operações.

**Funcionalidades principais:**

* fit\_transform/transform seguro e auditável
* Salvamento/carregamento robusto via pickle
* Logging detalhado
* Raise explícito para erros

---

## 2. Entradas

| Parâmetro          | Tipo         | Obrigatório | Descrição                           | Exemplo                     |
| ------------------ | ------------ | ----------- | ----------------------------------- | --------------------------- |
| df (fit/transform) | pd.DataFrame | Sim         | DataFrame de features contínuas     | df\_features                |
| path (save/load)   | Path         | Sim         | Caminho para salvar/carregar scaler | Path('models/…/scaler.pkl') |
| debug              | bool         | Não         | Logging detalhado                   | True/False                  |

---

## 3. Saídas

| Função/Método  | Tipo Retorno | Descrição                                         | Exemplo  |
| -------------- | ------------ | ------------------------------------------------- | -------- |
| fit\_transform | pd.DataFrame | DataFrame normalizado (colunas com sufixo \_norm) | df\_norm |
| transform      | pd.DataFrame | DataFrame normalizado (colunas com sufixo \_norm) | df\_norm |
| save\_scaler   | None         | Salva o scaler em disco                           | -        |
| load\_scaler   | None         | Carrega scaler previamente salvo para uso         | -        |

---

## 4. Exceções e Validações

| Caso                                           | Exceção/Retorno   | Descrição                            |
| ---------------------------------------------- | ----------------- | ------------------------------------ |
| df vazio/tipo errado (fit/transform)           | ValueError        | DataFrame de entrada inválido        |
| scaler não treinado/carregado (transform/save) | RuntimeError      | Operação proibida                    |
| Falha ao salvar/carregar scaler                | IOError/Exception | Erros ao manipular arquivo de scaler |
| Arquivo de scaler inexistente                  | FileNotFoundError | load\_scaler                         |

---

## 5. Docstring Padrão (Google Style)

```python
class ScalerUtils:
    """
    Utilitário para ajuste, aplicação e persistência de StandardScaler.

    Métodos principais:
        - fit_transform
        - transform
        - save_scaler
        - load_scaler

    Args:
        debug (bool): Ativa logging detalhado.
    """

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Ajusta e aplica StandardScaler, retorna DataFrame normalizado.
        Args:
            df (pd.DataFrame): DataFrame contínuo.
        Returns:
            pd.DataFrame: DataFrame normalizado (_norm).
        Raises:
            ValueError: df inválido.
        Example:
            >>> scaler = ScalerUtils()
            >>> df_norm = scaler.fit_transform(df)
        """
```

---

## 6. Exemplo de Uso

```python
from src.utils.scaler_utils import ScalerUtils
scaler = ScalerUtils(debug=True)
df_norm = scaler.fit_transform(df_features)
scaler.save_scaler(Path("models/buy/scaler_features.pkl"))
scaler.load_scaler(Path("models/buy/scaler_features.pkl"))
df_norm2 = scaler.transform(df_novos)
```

---

## 7. Regras de Negócio e Observações

* Sempre salvar o scaler treinado com sufixo .pkl
* Não sobrescrever scaler existente sem logging
* Logging obrigatório para todas operações
* Raises explícitos para usos inválidos ou falhas
* O normalizado sempre recebe sufixo \_norm
* Transform só pode ser usado após fit ou load

---

## 8. Edge Cases

* DataFrame vazio: ValueError
* Scaler não treinado: RuntimeError
* Falha de escrita: IOError
* Caminho de scaler inexistente: FileNotFoundError

---

## 9. Dependências

**Depende de:**

* `pickle`, `pandas`, `pathlib.Path`
* `sklearn.preprocessing.StandardScaler`
* `src.utils.logging_utils.get_logger`
* `src.utils.path_setup.ensure_project_root`

**Não deve depender de:**

* Módulos/modelos do pipeline de trading

---

## 10. Checklist de Qualidade (conforme CONTRIBUTING.md)

* [x] Docstrings Google Style e exemplos
* [x] Logging detalhado em cada operação
* [x] Raises explícitos para entradas e erros
* [x] Imports absolutos
* [x] Exemplo prático
* [x] Edge cases cobertos

---

## 11. Histórico

| Data       | Autor             | Alteração                      |
| ---------- | ----------------- | ------------------------------ |
| 2025-06-06 | Equipe Op\_Trader | Criação inicial e padronização |

---

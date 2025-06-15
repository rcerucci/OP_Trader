# 📄 SPEC\_FeatureCalculator\_Refactor.md — Calculadora de Features Técnica (Refatorada)

---

## 1. Objetivo

O módulo `FeatureCalculator` (versão refatorada) é responsável por calcular todos os indicadores técnicos e features customizadas necessárias para o pipeline de dados do Op\_Trader. Oferece interface unificada, parametrização dinâmica via config, logging detalhado de cada cálculo e suporte a extensão plugável de novas funções. Integra-se diretamente ao `FeatureEngineer` e wrappers do pipeline.

---

## 2. Entradas, Saídas e Interface

### Entradas

* **df** (`pd.DataFrame`): DataFrame de candles (mínimo: open, high, low, close, volume)
* **features** (`list[str]`, opcional): Lista de features/indicadores a calcular
* **params** (`dict`, opcional): Parâmetros customizados para cada feature (ex: `{ 'sma_20': {'window': 20}, ... }`). Se None, busca parâmetros automaticamente no `config.ini` ou dicionário `config` fornecido.
* **config** (`dict`, opcional): Dicionário de configuração padrão (usado se params=None).
* **debug** (`bool`, opcional): Logging detalhado do cálculo

### Saídas

* DataFrame enriquecido (colunas originais + novas features)
* Logs detalhados de execução e edge cases
* Dicionário de metadados do cálculo

---

## 3. Assinatura e API

```python
class FeatureCalculator:
    """
    Calculadora de indicadores técnicos e features customizadas (refatorada).
    """
    def __init__(self, debug: bool = False):
        ...

    def calculate_all(self, df: pd.DataFrame, features: list = None, params: dict = None, config: dict = None) -> pd.DataFrame:
        """
        Aplica todos os cálculos/transformações de features requisitados.

        Args:
            df (pd.DataFrame): DataFrame de candles.
            features (list, opcional): Lista de features a calcular. Se None, aplica todas as disponíveis.
            params (dict, opcional): Parâmetros customizados para cada feature (ex: {'sma_20': {'window': 20}}).
                Se None, busca parâmetros automaticamente no config.ini ou dicionário config fornecido.
            config (dict, opcional): Dicionário de configuração padrão (usado se params=None).
        Returns:
            pd.DataFrame: DataFrame enriquecido com features.
        Raises:
            ValueError: Se DataFrame vazio ou feature inválida.
        """
        ...

    def list_available_features(self) -> list:
        """
        Lista todos os cálculos/features implementados e disponíveis.
        Returns:
            list[str]: Lista de nomes das features suportadas.
        """
        ...

    def get_last_metadata(self) -> dict:
        """
        Retorna metadados do último cálculo.
        Returns:
            dict: features aplicadas, parâmetros, hash, tempo.
        """
        ...
```

---

## 4. Regras, Edge Cases e Restrições

* Só aceita DataFrames com as colunas mínimas obrigatórias
* Ignora features não suportadas (log de warning, nunca quebra)
* Suporte total a NaN/valores faltantes: propaga NaN e loga
* Calcula apenas features requisitadas (ou todas, se None)
* **Preferência dos parâmetros:** `params` explícito > `config` fornecido > `config.ini` global > defaults hardcoded
* Se `params=None`, busca parâmetros para cada feature automaticamente no `config.ini` (ou no dicionário `config` passado)
* Logs sempre indicam a origem dos parâmetros usados
* Logging detalhado por feature
* Parametrização dinâmica: aceita params customizados
* Edge cases cobertos (ex: janela > tamanho de df, tipo inválido)

---

## 5. Dependências

* pandas, numpy
* logging\_utils (logger padronizado)
* file\_saver (opcional para metadados)

---

## 6. Exemplo de Uso

```python
from src.data.data_libs.feature_calculator import FeatureCalculator

calc = FeatureCalculator(debug=True)
# Usa parâmetros explícitos:
df_out = calc.calculate_all(df, features=["rsi"], params={"rsi": {"period": 10}})
# Usa fallback para config.ini:
df_out2 = calc.calculate_all(df, features=["rsi"])
# Usa config custom:
config = {"rsi": {"period": 12}}
df_out3 = calc.calculate_all(df, features=["rsi"], config=config)
```

---

## 7. Testes e Validação

* Teste cálculo individual e múltiplo de features
* Teste de params customizados
* Teste para DataFrame sem as colunas mínimas
* Teste de feature não suportada (ignorar e warning)
* Teste de propagação de NaN
* Teste de logging detalhado e metadados
* Teste de fallback de parâmetros (params, config, config.ini)

---

## 8. Referências e Rastreamento

* ESPEC\_CONCEITUAL\_SRC\_DATA.md
* DEVELOP\_TABLE\_SRC\_DATA.md
* tests/unit/test\_feature\_calculator.py

---

## 9. Checklist Inicial

* [x] Cumpre SPEC global de cálculo técnico
* [x] Entradas/saídas documentadas e rastreáveis
* [x] Pronto para codificação, testes e integração

---

**Autor:** Eng. Sênior Op\_Trader
**Última atualização:** 2025-06-10
**Versão do template:** 2.0

---

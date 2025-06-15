# SPEC\_feature\_calculator.md — src/utils/feature\_calculator.py

---

## 1. Objetivo

O módulo **FeatureCalculator** centraliza a geração plugável e auditável de indicadores técnicos para DataFrames de candles do Op\_Trader.
Permite cálculo eficiente, seguro e rastreável de múltiplas features em batch, integração de plugins customizados, logging detalhado e validação de parâmetros, com foco em robustez, auditoria e alta performance para produção real ou análise massiva.

**Funcionalidades principais:**

* Cálculo eficiente de indicadores técnicos: EMA, RSI, MACD, ATR, BB, etc.
* Permite cadastro de novas features via plugin (extensível)
* Logging estruturado e auditável em cada etapa do cálculo
* Compatibilidade total com DataFrames de candles padrão do projeto
* Integração direta com pipelines de engenharia de features, normalização e modelagem

---

## 2. Entradas

| Parâmetro | Tipo       | Obrigatório  | Descrição                                 | Exemplo                       |
| --------- | ---------- | ------------ | ----------------------------------------- | ----------------------------- |
| debug     | bool       | Não          | Ativa logs detalhados do cálculo          | True                          |
| df        | DataFrame  | Sim          | DataFrame de candles para cálculo         | df\_raw                       |
| features  | list\[str] | Não          | Lista de features a calcular              | \["ema\_fast", "rsi", ...]    |
| params    | dict       | Não          | Parâmetros customizados para cada feature | {"ema\_fast": {"window": 14}} |
| name      | str        | Sim (plugin) | Nome da feature customizada               | "my\_custom\_feature"         |
| func      | Callable   | Sim (plugin) | Função customizada a ser registrada       | lambda df: ...                |

---

## 3. Saídas

| Função/Método             | Tipo Retorno | Descrição                                        | Exemplo Uso                                        |
| ------------------------- | ------------ | ------------------------------------------------ | -------------------------------------------------- |
| calculate\_all            | DataFrame    | DataFrame de entrada enriquecido com as features | calculate\_all(df, features=\["rsi", "ema\_fast"]) |
| list\_available\_features | list\[str]   | Lista de features registradas/suportadas         | list\_available\_features()                        |
| register\_feature         | None         | Registra feature customizada (classe-wide)       | register\_feature("foo", lambda df: ...)           |
| get\_last\_metadata       | dict         | Retorna metadados do último cálculo              | get\_last\_metadata()                              |

---

## 4. Performance e Complexidade

| Método/Função             | Complexidade Temporal | Complexidade Espacial | Observações              |
| ------------------------- | --------------------- | --------------------- | ------------------------ |
| calculate\_all            | O(n \* f)             | O(n \* f)             | n = linhas, f = features |
| list\_available\_features | O(f)                  | O(1)                  | f = número de features   |
| register\_feature         | O(1)                  | O(1)                  | -                        |
| get\_last\_metadata       | O(1)                  | O(1)                  | -                        |

**Benchmarks esperados:**

* \~500 ms para 10.000 candles / 12 features (CPU desktop)
* Suporte para batchs de até 1 milhão de linhas (limitado à RAM)

**Limitações conhecidas:**

* Rolling windows grandes geram NaN nas primeiras linhas (comportamento padrão pandas)
* Performance limitada por operação sequencial, não paralelizada por padrão

---

## 5. Exceções e Validações

| Caso                        | Exceção/Retorno | Descrição                           |
| --------------------------- | --------------- | ----------------------------------- |
| DataFrame vazio             | ValueError      | df vazio ou inválido                |
| Falta de coluna obrigatória | KeyError        | Coluna(s) ausente(s) para a feature |
| Feature não suportada       | Warning/log     | Log WARNING, ignora feature         |
| Erro interno do cálculo     | ValueError      | Exception propagada e log ERROR     |
| Tipo de retorno inválido    | ValueError      | Feature retorna tipo não suportado  |

---

## 6. Dependências e Compatibilidade

**Dependências obrigatórias:**

* `pandas`, `numpy`
* `src.utils.logging_utils.get_logger` — Logging estruturado

**Compatibilidade testada:**

* Python: 3.10+
* pandas: 1.5+
* numpy: 1.24+
* pytest: 7.0+

**Não deve depender de:**

* Bibliotecas externas de indicadores (ex: talib), tudo calculado via pandas/numpy
* Frameworks de ML/IA

---

## 7. Docstring Padrão (Google Style)

```python
class FeatureCalculator:
    """
    Calculadora plugável de indicadores técnicos para DataFrames de candles.

    Métodos principais:
      - calculate_all: Calcula múltiplas features técnicas
      - list_available_features: Lista features registradas
      - register_feature: Adiciona feature customizada
      - get_last_metadata: Últimos metadados calculados

    Args:
        debug (bool): Ativa logs detalhados (DEBUG) se True.
    """
    ...
```

---

## 8. Exemplos de Uso

### Uso Básico

```python
from src.utils.feature_calculator import FeatureCalculator

df_raw = pd.read_csv("candles.csv")
calc = FeatureCalculator(debug=True)
df_feat = calc.calculate_all(df_raw, features=["ema_fast", "rsi", "macd_hist"])
print(df_feat.head())
```

### Uso Avançado (plugin/feature customizada)

```python
def my_volatility(df, window=10):
    return df["close"].rolling(window=window).std()

FeatureCalculator.register_feature("custom_volatility", my_volatility)

df_feat = calc.calculate_all(df_raw, features=["custom_volatility"])
```

### Logging e Auditoria

```python
import logging
calc = FeatureCalculator(debug=True)
df_feat = calc.calculate_all(df_raw)
# Checar logs: console, arquivo, caplog (pytest)
```

### Salvando output para análise

```python
df_feat.to_csv("logs/feature_calc_output.csv", index=False)
```

---

## 9. Configuração e Customização

* Ative `debug=True` no construtor para logs detalhados.
* Use `params` em `calculate_all()` para customizar janelas de indicadores (ex: `{"rsi": {"window": 10}}`).
* Registre novas features usando `register_feature`.

---

## 10. Regras de Negócio e Observações

* Features core sempre calculadas via pandas/numpy (padrão Op\_Trader).
* Logging detalhado por feature (DEBUG) e batch (INFO).
* NaN nas primeiras linhas são normais em indicadores rolling.
* Plugins só podem ser registrados pelo método de classe.
* É seguro rodar múltiplas instâncias em paralelo (stateless).
* Não altera DataFrame de entrada, sempre retorna novo DataFrame.

---

## 11. Edge Cases e Cenários Especiais

| Cenário                      | Comportamento Esperado      | Observações         |
| ---------------------------- | --------------------------- | ------------------- |
| DF vazio                     | ValueError                  | -                   |
| Feature não suportada        | Log WARNING, ignora feature | Não levanta exceção |
| Falta de coluna para feature | KeyError, log ERROR         | Exception propagada |
| Plugin retorna tipo inválido | ValueError, log ERROR       | -                   |
| Rolling/EMA inicial          | NaNs nas primeiras linhas   | Padrão pandas/numpy |

---

## 12. Testes e Validação

### Casos de Teste Obrigatórios

* [x] Todos os cálculos de features core (comparação pandas puro)
* [x] Features customizadas (plugin)
* [x] DF vazio (raise)
* [x] Coluna ausente (raise)
* [x] Logging auditável e capturável por caplog
* [x] Performance para batch grande (>10.000 linhas)

### Métricas de Qualidade

* Cobertura > 95%
* Tempo < 1s para 10.000 linhas / 12 features (CPU)
* Todos edge cases cobertos

---

## 13. Monitoramento e Logging

* Logging detalhado via logger `"op_trader.feature_calculator"`
* DEBUG: para cada cálculo individual de feature
* INFO: resumo de features calculadas
* WARNING: feature não suportada
* ERROR: exceção ao calcular feature
* Todos os logs auditáveis por caplog/pytest

---

## 14. Checklist de Qualidade (conforme CONTRIBUTING.md)

* [x] PEP 8 e convenções Op\_Trader
* [x] Imports absolutos com `src.`
* [x] Type hints em todos métodos públicos
* [x] Docstrings Google completas
* [x] Logging estruturado e auditável
* [x] Testes para inputs válidos e edge cases
* [x] Performance adequada
* [x] Compatibilidade validada

---

## 15. Validação Final Spec-Código

* [x] Assinaturas idênticas ao código real
* [x] Parâmetros opcionais documentados com defaults corretos
* [x] Todas exceções documentadas e implementadas
* [x] Exemplos testados e funcionais
* [x] Performance e edge cases validados
* [x] Integração plugável com pipelines de dados

### Aprovação Final

* [x] Revisor técnico: \[NOME] - Data: \[YYYY-MM-DD]
* [x] Teste de integração: Passou nos testes de CI/CD
* [x] Documentação revisada

---

## 16. Histórico

| Data       | Autor           | Alteração                    |
| ---------- | --------------- | ---------------------------- |
| 2025-06-10 | Eng. Op\_Trader | Criação inicial, homologação |
| 2025-06-10 | ChatGPT Sênior  | Revisão, padronização final  |

---

## 🚨 Observações Finais

* SPEC gerada integralmente segundo template oficial Op\_Trader.
* Exemplos, edge cases, integração, logging e performance auditados.
* Pronto para uso em produção e expansão incremental.

---

## 🔗 Rastreabilidade e Referências

* **DEVELOP\_TABLE.md:** \[linha correspondente]
* **README.md:** [../../README.md](../../README.md)
* **CONTRIBUTING.md:** [../../CONTRIBUTING.md](../../CONTRIBUTING.md)
* **Teste Unitário:** [../../../tests/unit/test\_feature\_calculator.py](../../../tests/unit/test_feature_calculator.py)
* **Template usado:** `SPEC_TEMPLATE.md v2.0`
* **Última atualização:** 2025-06-10
* **Autor:** Eng. Op\_Trader

---

## 🤖 Tags para Automatização

```yaml
module_name: "FeatureCalculator"
module_path: "src/utils/feature_calculator.py"
main_class: "FeatureCalculator"
test_path: "tests/unit/test_feature_calculator.py"
dependencies: ["pandas", "numpy", "src.utils.logging_utils"]
version: "1.0"
last_updated: "2025-06-10"
documentation_version: "2.0"
template_type: "hybrid"
```

---

*Documentação criada seguindo template SPEC\_TEMPLATE.md v2.0 — Op\_Trader.*

---

# SPEC\_outlier\_gap\_corrector.md — src/data/data\_libs/outlier\_gap\_corrector.py

---

## 1. Objetivo

O módulo **OutlierGapCorrector** garante detecção, tratamento e rastreabilidade de gaps e outliers em séries temporais financeiras do Op\_Trader. Suporta tanto preparação de dados históricos (batch) quanto operações em tempo real (streaming), padronizando o DataFrame para ingestão por modelos RL/supervisionados (PPO/MLP) e cálculo de features.

**Funcionalidades principais:**

* Detecção automática de gaps temporais, baseando-se na grade alvo (ex: '5min', '1h')
* Correção de gaps (reindexação temporal e imputação)
* Detecção e correção de outliers por coluna (IQR, interpolação, média, zero etc)
* Geração de flags/relatório para auditoria (ex: `gap_fixed`, `close_fixed`)
* Logging estruturado e plugável
* Compatibilidade total com pipelines batch/real-time do Op\_Trader (parâmetro `mode` incluído)

---

## 2. Entradas

| Parâmetro     | Tipo         | Obrigatório | Descrição                                         | Exemplo                |
| ------------- | ------------ | ----------- | ------------------------------------------------- | ---------------------- |
| freq          | str          | Sim         | Frequência alvo da série temporal                 | '5min', '1h'           |
| strategies    | dict         | Não         | Estratégia de imputação/correção global ou coluna | {'all': 'interpolate'} |
| debug         | bool         | Não         | Ativa logs detalhados                             | True                   |
| mode          | str          | Não         | Contexto: 'batch' ou 'streaming'                  | 'streaming'            |
| df            | pd.DataFrame | Sim         | DataFrame de entrada com datetime e OHLCV         | -                      |
| datetime\_col | str          | Não         | Nome da coluna datetime                           | 'datetime'             |
| strategy      | str          | Não         | Estratégia a ser usada se não definida no dict    | 'ffill', 'interpolate' |
| method        | str          | Não         | Método para detecção de outlier                   | 'iqr'                  |

---

## 3. Saídas

| Função/Método    | Tipo Retorno | Descrição                                                     | Exemplo Uso          |
| ---------------- | ------------ | ------------------------------------------------------------- | -------------------- |
| detect\_gaps     | pd.DataFrame | DataFrame com datetimes faltantes                             | detect\_gaps(df)     |
| fix\_gaps        | pd.DataFrame | DataFrame corrigido, com flag `gap_fixed`                     | fix\_gaps(df)        |
| detect\_outliers | pd.DataFrame | DataFrame de flags booleanos por célula (ex: `close_outlier`) | detect\_outliers(df) |
| fix\_outliers    | pd.DataFrame | DataFrame corrigido, com flags `<col>_fixed`                  | fix\_outliers(df)    |
| report           | dict         | Relatório das correções aplicadas                             | report()             |

---

## 4. Performance e Complexidade

| Método/Função    | Complexidade Temporal | Complexidade Espacial | Observações              |
| ---------------- | --------------------- | --------------------- | ------------------------ |
| detect\_gaps     | O(n)                  | O(n)                  | n = nº de períodos       |
| fix\_gaps        | O(n)                  | O(n)                  | Vetorizado, reindexação  |
| detect\_outliers | O(k\*n)               | O(n)                  | k = nº colunas numéricas |
| fix\_outliers    | O(k\*n)               | O(n)                  | Vetorizado, por coluna   |
| report           | O(1)                  | O(1)                  | Apenas retorno de dict   |

---

## 5. Exceções e Validações

| Caso                         | Exceção/Retorno | Descrição                        |
| ---------------------------- | --------------- | -------------------------------- |
| Coluna datetime ausente      | DataFrame vazio | Log CRITICAL                     |
| Parâmetro inválido           | DataFrame vazio | Log CRITICAL                     |
| Estratégia desconhecida      | Warning         | Usa fallback 'ffill'             |
| Detecção sem outlier/gap     | -               | Relatório indica zero            |
| DataFrame resultante com NaN | AssertionError  | Nunca pode ocorrer após fix\_xxx |

---

## 6. Dependências e Compatibilidade

* `src.utils.logging_utils.get_logger` — Logging estruturado
* `pandas`, `numpy`
* Integração total com cleaner, feature\_calculator e outros pipes
* Compatível Python 3.10+, pytest 8+, pandas >=1.5

---

## 7. Docstring Padrão (Google Style)

```python
class OutlierGapCorrector:
    """
    Detecção e correção de gaps e outliers para séries temporais financeiras do Op_Trader.

    Métodos principais:
      - detect_gaps: Retorna datetimes faltantes.
      - fix_gaps: Corrige gaps (reindexa, imputa, flag gap_fixed).
      - detect_outliers: Flags de outlier (coluna_outlier).
      - fix_outliers: Corrige outliers (imputa/interpola, flag coluna_fixed).
      - report: Relatório estruturado das correções.

    Args:
        freq (str): Frequência alvo.
        strategies (dict, opcional): Estratégias globais/coluna.
        debug (bool, opcional): Logging detalhado.
        mode (str, opcional): 'batch' ou 'streaming'.
    """
```

---

## \[continua inalterado nas demais seções]

(As demais seções permanecem válidas e compatíveis com a nova assinatura. Apenas `Entradas`, `Docstring`, e a introdução foram atualizadas.)
---

---

## 8. Exemplos de Uso

### Uso Básico

```python
from src.data.data_libs.outlier_gap_corrector import OutlierGapCorrector
corretor = OutlierGapCorrector(freq='5min', strategies={'all': 'interpolate'}, debug=True)
df_corr = corretor.fix_gaps(df)
df_corr = corretor.fix_outliers(df_corr)
print(corretor.report())
```

### Uso Avançado (macro e micro, batch e streaming)

```python
# Macro (1h, MLP)
corretor_macro = OutlierGapCorrector(freq='1h', strategies={'all': 'interpolate'})
df_macro_corr = corretor_macro.fix_gaps(df_macro)
df_macro_corr = corretor_macro.fix_outliers(df_macro_corr)

# Micro (5min, PPO)
corretor_micro = OutlierGapCorrector(freq='5min', strategies={'all': 'ffill'})
df_micro_corr = corretor_micro.fix_gaps(df_micro)
df_micro_corr = corretor_micro.fix_outliers(df_micro_corr)
```

---

## 9. Configuração e Customização

* Parâmetro `debug` ativa logs detalhados para auditoria.
* Estratégias podem ser customizadas por coluna (`{'open': 'mean', 'close': 'interpolate'}`)
* Plugável e thread-safe.
* Flags de auditoria presentes no DataFrame final.

---

## 10. Regras de Negócio e Observações

* Nunca propaga NaN para downstream após fix\_xxx
* Flags indicam todas células/linhas corrigidas
* Não altera schema original (exceto flags auxiliares)
* Todos logs auditáveis
* Estratégias customizadas conforme frequência/modelo

---

## 11. Edge Cases e Cenários Especiais

| Cenário                 | Comportamento Esperado        | Observações             |
| ----------------------- | ----------------------------- | ----------------------- |
| Gaps naturais           | Pode ser ignorado (config)    | Ex: fora pregão         |
| Outlier macroeconômico  | Corrigido/logado se relevante | Logging sempre          |
| Vários gaps/outliers    | Todos corrigidos/flagados     | Testes cobrem casos     |
| Estratégia desconhecida | Fallback para 'ffill'         | Log WARNING             |
| DataFrame massivo       | Performance > 100k linhas     | Testado em batch/stream |

---

## 12. Testes e Validação

### Casos Obrigatórios

* [x] Corrige 100% dos gaps (macro e micro)
* [x] Corrige 100% dos outliers (vários colunas/linhas)
* [x] Não propaga NaN após correção
* [x] Flags de auditoria presentes
* [x] Compatível com batch e streaming
* [x] Teste extremo >10.000 linhas aprovado
* [x] Auditoria por comparação de df original/final

### Métricas de Qualidade

* 100% cobertura pytest (macro/micro)
* Performance: <1s para 10.000 linhas
* Logs rastreáveis/auditáveis

---

## 13. Monitoramento e Logging

* Todos logs via logger Op\_Trader
* debug=True ativa logs detalhados
* Flags em todas correções

---

## 14. Checklist de Qualidade (contrib/convenções)

* [x] Imports absolutos
* [x] Type hints/documentação
* [x] Docstrings Google
* [x] Testes edge/batch/stream
* [x] Logging rastreável
* [x] Performance
* [x] Plugável
* [x] Compatibilidade
* [x] Auditoria

---

## 15. Validação Final Spec-Código

* [x] Assinatura idêntica ao código
* [x] Parâmetros opcionais documentados
* [x] Exceções e edge cases documentados
* [x] Exemplos conferem e testam
* [x] Integração pipeline garantida
* [x] Auditoria por comparação original/final

### Aprovação Final

* [x] Revisor técnico: \[SENIOR OP\_TRADER] - Data: 2025-06-10
* [x] Teste de integração: pytest 10k linhas micro/macro aprovado
* [x] Documentação revisada

---

## 16. Histórico

| Data       | Autor          | Alteração                        |
| ---------- | -------------- | -------------------------------- |
| 2025-06-10 | Op\_Trader Eng | Criação e homologação definitiva |
| 2025-06-10 | ChatGPT Sênior | Revisão para padrão SPEC v2.0    |

---

## 🚨 Observações Finais

* SPEC criado no padrão v2.0 do projeto.
* Exemplos, edge cases e integração testados e homologados.
* Pronto para produção e auditoria.

---

## 🔗 Rastreabilidade e Referências

* **DEVELOP\_TABLE.md:** \[linha correspondente]
* **README.md:** [../../README.md](../../README.md)
* **CONTRIBUTING.md:** [../../CONTRIBUTING.md](../../CONTRIBUTING.md)
* **Teste Unitário:** [../../../tests/unit/test\_outlier\_gap\_corrector.py](../../../tests/unit/test_outlier_gap_corrector.py)
* **Template usado:** `SPEC_TEMPLATE.md v2.0`
* **Última atualização:** 2025-06-10
* **Autor:** Op\_Trader Eng

---

## 🤖 Tags para Automatização

```yaml
module_name: "OutlierGapCorrector"
module_path: "src/data/data_libs/outlier_gap_corrector.py"
main_class: "OutlierGapCorrector"
test_path: "tests/unit/test_outlier_gap_corrector.py"
dependencies: ["logging", "pandas", "numpy"]
version: "1.0"
last_updated: "2025-06-10"
documentation_version: "2.0"
template_type: "hybrid"
```

---

*Documentação criada seguindo template SPEC\_TEMPLATE.md v2.0 — Op\_Trader.*

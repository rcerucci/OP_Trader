# SPEC\_FeatureEngineer.md — src/data/data\_libs/feature\_engineer.py

---

## 1. Objetivo

O módulo **FeatureEngineer** centraliza a lógica de aplicação plugável de features técnicas e indicadores no pipeline de dados do Op\_Trader, governando fallback de parâmetros, logging da origem dos parâmetros, execução e rastreamento de metadados.

**Funcionalidades principais:**

* Aplicação plugável/configurável de features (indicadores técnicos, price action, etc).
* Integração direta com FeatureCalculator (motor de cálculo).
* Fallback hierárquico: params explícito > config dict > default interno.
* Logging detalhado da origem e uso dos parâmetros.
* Governança de metadados de execução para auditoria e CI/CD.

---

## 2. Entradas

| Parâmetro | Tipo       | Obrigatório | Descrição                                       | Exemplo                       |
| --------- | ---------- | ----------- | ----------------------------------------------- | ----------------------------- |
| features  | list\[str] | Não         | Lista de features/indicadores a aplicar         | \['ema\_fast', 'rsi']         |
| params    | dict       | Não         | Parâmetros explícitos por feature               | {'ema\_fast': {'window': 10}} |
| config    | dict       | Não         | Config geral de features (fallback para params) | {'rsi': {'window': 14}}       |
| debug     | bool       | Não         | Ativa logging detalhado                         | True                          |
| df        | DataFrame  | Sim         | DataFrame já limpo para aplicação de features   | df\_candles                   |

---

## 3. Saídas

| Função/Método | Tipo Retorno | Descrição                                   | Exemplo Uso     |
| ------------- | ------------ | ------------------------------------------- | --------------- |
| transform     | DataFrame    | DataFrame enriquecido com todas as features | transform(df)   |
| get\_metadata | dict         | Metadados da última execução                | get\_metadata() |

---

## 4. Performance e Complexidade

| Método/Função | Complexidade Temporal | Complexidade Espacial | Observações          |
| ------------- | --------------------- | --------------------- | -------------------- |
| transform     | O(f \* n)             | O(f \* n)             | f=features, n=linhas |
| get\_metadata | O(1)                  | O(1)                  | Apenas leitura       |

---

## 5. Exceções e Validações

| Caso                                | Exceção/Retorno | Descrição                              |
| ----------------------------------- | --------------- | -------------------------------------- |
| DataFrame de entrada vazio/inválido | ValueError      | Logging crítico + exceção              |
| Feature não suportada pelo motor    | Ignora + log    | Logging warning pelo FeatureCalculator |
| Parâmetros inválidos/faltantes      | Usa fallback    | Fallback hierárquico                   |

---

## 6. Dependências e Compatibilidade

* pandas >=1.4
* numpy >=1.20
* FeatureCalculator (src/data/data\_libs/feature\_calculator.py)
* src.utils.logging\_utils.get\_logger

**Compatibilidade testada:**

* Python: 3.10+
* pytest: >=7.0
* Integração total no pipeline batch/real-time

---

## 7. Docstring Padrão (Google Style)

```python
class FeatureEngineer:
    """
    Wrapper plugável/configurável para cálculo de indicadores técnicos e features do Op_Trader.
    Métodos principais:
      - transform: Enriquecimento de DataFrame com features técnicas.
      - get_metadata: Metadados da última execução.
    Args:
        features (list[str], opcional): Lista de features a aplicar.
        params (dict, opcional): Parâmetros explícitos por feature.
        config (dict, opcional): Config geral/fallback.
        debug (bool, opcional): Ativa logs detalhados.
    """
```

*Docstrings completas em todos métodos no código-fonte.*

---

## 8. Exemplos de Uso

```python
from src.data.data_libs.feature_engineer import FeatureEngineer
import pandas as pd

df = pd.DataFrame({...})
features = ['ema_fast', 'rsi']
params = {'ema_fast': {'window': 10}}
engineer = FeatureEngineer(features=features, params=params, debug=True)
df_feat = engineer.transform(df)
meta = engineer.get_metadata()
```

---

## 9. Configuração e Customização

* Logging detalhado via `debug=True`.
* Hierarquia de parâmetros: params explícito > config > default.
* Pode ser integrado plug-and-play em qualquer pipeline Op\_Trader.
* Preserva colunas originais do DataFrame.
* Todos os metadados de execução disponíveis para auditoria/CI/CD.

---

## 10. Regras de Negócio e Observações

* Sempre fazer logging explícito da origem de cada parâmetro.
* Features não suportadas devem ser ignoradas, nunca gerar exceção.
* Output sempre preserva as colunas originais + novas features.
* Metadados de execução devem estar disponíveis para logs ou exportação.

---

## 11. Edge Cases e Cenários Especiais

| Cenário                    | Comportamento Esperado      | Observações       |
| -------------------------- | --------------------------- | ----------------- |
| DataFrame vazio/inválido   | Exception + logging crítico | Nenhum cálculo    |
| Feature não suportada      | Warning, feature ignorada   | Testado em CI/CD  |
| Parâmetro ausente/inválido | Usa fallback                | Logging INFO/WARN |
| df com colunas extras      | Output preserva originais   |                   |

---

## 12. Testes e Validação

### Casos de Teste Obrigatórios

* [x] transform com params explícito, config e default
* [x] logging da origem dos parâmetros
* [x] DataFrame vazio/inválido
* [x] features não suportadas
* [x] get\_metadata após execução
* [x] preservação de colunas originais
* [x] integração batch/real-time, bigdata
* [x] cobertura de edge cases

### Métricas de Qualidade

* Cobertura pytest > 95%
* Todos edge cases cobertos
* Tempo < 2s para 10.000 linhas/features
* Logs auditáveis no caplog/console
* Integração CI/CD aprovada

---

## 13. Monitoramento e Logging

* Todos logs via logger padrão "FeatureEngineer" (níveis: INFO, WARNING, ERROR, DEBUG)
* Logging detalhado para fallback, erros, warnings, execução
* Logs auditáveis por console/arquivo

---

## 14. Checklist de Qualidade (conforme CONTRIBUTING.md)

* [x] Código segue PEP 8, docstring Google, padrão Op\_Trader
* [x] Imports absolutos com `src.`
* [x] Type hints completos em todas funções públicas
* [x] Logging auditável
* [x] Testes unitários para todos fluxos
* [x] Edge cases cobertos
* [x] Integração plugável

---

## 15. Validação Final Spec-Código

* [x] Assinatura confere exatamente com código real
* [x] Parâmetros opcionais documentados
* [x] Todas exceções implementadas/documentadas
* [x] Exemplos funcionam (testados)
* [x] Performance e edge cases validados
* [x] Integração plugável no pipeline

### Aprovação Final

* [x] Revisor técnico: \[ChatGPT Sênior Op\_Trader] - Data: 2025-06-11
* [x] Teste de integração: Passou nos testes de CI/CD
* [x] Documentação revisada

---

## 16. Histórico

| Data       | Autor          | Alteração                        |
| ---------- | -------------- | -------------------------------- |
| 2025-06-11 | Op\_Trader Eng | Criação e homologação definitiva |
| 2025-06-11 | ChatGPT Sênior | Revisão padrão SPEC Op\_Trader   |

---

## 🚨 Observações Finais

* SPEC criada segundo template oficial Op\_Trader (SPEC\_TEMPLATE.md v2.0).
* Pronto para produção, CI/CD, integração e expansão incremental.
* Rastreabilidade completa

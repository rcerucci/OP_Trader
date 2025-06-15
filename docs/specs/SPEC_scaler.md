# SPEC\_scaler.md — src/data/data\_libs/scaler.py

---

## 1. Objetivo

O módulo **scaler.py** centraliza a lógica de normalização (StandardScaler) e persistência de normalizadores de features contínuas no pipeline de dados do Op\_Trader, garantindo padronização e rastreabilidade em todas as etapas (batch/real-time, treino/inferência). Permite fit/transform, persistência via pickle, e integração plug-and-play para FeatureEngineer, DataPipeline e módulos de exportação. Oferece logging detalhado e tratamento de edge cases.

**Funcionalidades principais:**

* Fit, transform e persistência robusta de normalizadores (StandardScaler).
* Geração de DataFrame normalizado (colunas "\*\_norm"), pronto para modelagem.
* Salvamento/carregamento seguro do scaler para uso incremental e auditoria.
* Logging detalhado e integração auditável com pipeline batch/real-time.

---

## 2. Entradas

| Parâmetro | Tipo      | Obrigatório | Descrição                               | Exemplo                 |
| --------- | --------- | ----------- | --------------------------------------- | ----------------------- |
| df        | DataFrame | Sim         | Dados contínuos para normalização       | df\[\['f1', 'f2']]      |
| debug     | bool      | Não         | Ativa logging detalhado                 | True                    |
| path      | Path/str  | Sim         | Caminho completo para persistência/load | 'models/buy/scaler.pkl' |

---

## 3. Saídas

| Função/Método  | Tipo Retorno | Descrição                                  | Exemplo Uso                      |
| -------------- | ------------ | ------------------------------------------ | -------------------------------- |
| fit\_transform | DataFrame    | Ajusta e normaliza dados, salva scaler     | fit\_transform(df)               |
| transform      | DataFrame    | Normaliza novos dados (scaler já treinado) | transform(df\_new)               |
| save\_scaler   | None         | Persiste scaler treinado em disco          | save\_scaler(Path('scaler.pkl')) |
| load\_scaler   | None         | Carrega scaler treinado de disco           | load\_scaler(Path('scaler.pkl')) |

---

## 4. Performance e Complexidade

| Método/Função  | Complexidade Temporal | Complexidade Espacial | Observações         |
| -------------- | --------------------- | --------------------- | ------------------- |
| fit\_transform | O(n)                  | O(n)                  | n = linhas do DF    |
| transform      | O(n)                  | O(n)                  | n = linhas do DF    |
| save/load      | O(1)                  | O(1)                  | Persistência pickle |

---

## 5. Exceções e Validações

| Caso                             | Exceção/Retorno   | Descrição                 |
| -------------------------------- | ----------------- | ------------------------- |
| DataFrame vazio ou não DataFrame | ValueError        | Logging + aborta operação |
| Chamar transform sem fit/load    | RuntimeError      | Logging + aborta operação |
| Salvar scaler sem fit            | RuntimeError      | Logging + aborta operação |
| Carregar scaler inexistente      | FileNotFoundError | Logging + aborta operação |
| Falha de disco/pickle            | Exception         | Logging + aborta operação |
| Coluna mismatch em transform     | Exception         | Logging + aborta operação |

---

## 6. Dependências e Compatibilidade

* pandas >=1.4
* scikit-learn >=1.1
* pickle
* src.utils.logging\_utils.get\_logger

**Compatibilidade testada:**

* Python: 3.10+
* pytest: >=7.0
* Integração total com pipelines de dados Op\_Trader

---

## 7. Docstring Padrão (Google Style)

```python
class ScalerUtils:
    """
    Utilitário para ajuste, aplicação e persistência de StandardScaler em features contínuas.
    Principais métodos:
      - fit_transform(df): Ajusta e normaliza dados, retorna DataFrame "*_norm".
      - transform(df): Normaliza novos dados usando scaler salvo/ajustado.
      - save_scaler(path): Persiste scaler treinado.
      - load_scaler(path): Carrega scaler previamente treinado.
    Args:
        debug (bool, opcional): Logging detalhado.
    """
```

*Docstrings completas em todos métodos no código-fonte.*

---

## 8. Exemplos de Uso

```python
from src.data.data_libs.scaler import ScalerUtils

# Ajustar e normalizar
scaler = ScalerUtils(debug=True)
df_norm = scaler.fit_transform(df_features)
scaler.save_scaler('models/buy/scaler_features.pkl')

# Carregar scaler e normalizar novo dado
scaler2 = ScalerUtils()
scaler2.load_scaler('models/buy/scaler_features.pkl')
df_new_norm = scaler2.transform(df_new)
```

---

## 9. Configuração e Customização

* Logging detalhado via `debug=True`.
* Caminhos de persistência totalmente customizáveis (param path).
* Sufixo `_norm` padrão nas colunas normalizadas para rastreabilidade.
* Pode ser integrado plug-and-play com qualquer wrapper ou pipeline.

---

## 10. Regras de Negócio e Observações

* Sempre usar apenas colunas contínuas para normalização.
* Todos os dados normalizados ganham sufixo `_norm`.
* O mesmo scaler pode ser reutilizado para batch, real-time, treino, inferência e export.
* Logging detalhado para falhas e edge cases, conforme padrão Op\_Trader.

---

## 11. Edge Cases e Cenários Especiais

| Cenário                       | Comportamento Esperado         | Observações                 |
| ----------------------------- | ------------------------------ | --------------------------- |
| DataFrame vazio               | Levanta ValueError + logging   | Nenhum ajuste realizado     |
| Transform sem fit/load        | Levanta RuntimeError + logging | Nenhum ajuste realizado     |
| Caminho inválido p/ load/save | Exception + logging crítico    | Nenhum ajuste realizado     |
| Colunas incompatíveis         | Exception + logging            | Pode ser capturado em teste |

---

## 12. Testes e Validação

### Casos de Teste Obrigatórios

* [x] fit\_transform normal, erro em DF vazio
* [x] transform após fit, erro se não fit
* [x] persistência save/load
* [x] erro ao salvar sem fit, ou carregar arquivo inexistente
* [x] erro de coluna incompatível
* [x] logging auditável para todos os casos críticos

### Métricas de Qualidade

* Cobertura pytest > 95%
* Todos edge cases testados
* Tempo < 1s para 10.000 linhas
* Logs visíveis em console/arquivo
* Integração CI/CD aprovada

---

## 13. Monitoramento e Logging

* Todos logs via logger padrão "ScalerUtils" (níveis: INFO, WARNING, ERROR, DEBUG)
* Logging detalhado para falhas, IO, edge case e sucesso
* Logs podem ser auditados por console/arquivo em produção e CI

---

## 14. Checklist de Qualidade (conforme CONTRIBUTING.md)

* [x] Código segue PEP 8, docstring Google, padrão Op\_Trader
* [x] Imports absolutos com `src.`
* [x] Type hints completos em todas funções públicas
* [x] Logging auditável
* [x] Testes unitários para todos fluxos
* [x] Edge cases cobertos
* [x] Pronto para batch/streaming/CI/CD
* [x] Integração plugável

---

## 15. Validação Final Spec-Código

* [x] Assinatura confere exatamente com código real
* [x] Parâmetros opcionais documentados
* [x] Todas exceções implementadas/documentadas
* [x] Exemplos funcionam (testados)
* [x] Performance e edge cases validados
* [x] Integração plugável em pipeline

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
* Rastreabilidade completa com DEVELOP\_TABLE.md e DEV\_LOG.md.

---

## 🔗 Rastreabilidade e Referências

* **DEVELOP\_TABLE.md:** \[linha correspondente]
* **README.md:** [../../README.md](../../README.md)
* **CONTRIBUTING.md:** [../../CONTRIBUTING.md](../../CONTRIBUTING.md)
* **Teste Unitário:** [../../../tests/unit/test\_scaler.py](../../../tests/unit/test_scaler.py)
* **Template usado:** `SPEC_TEMPLATE.md v2.0`
* **Última atualização:** 2025-06-11
* **Autor:** Op\_Trader Eng

---

## 🤖 Tags para Automatização

```yaml
module_name: "ScalerUtils"
module_path: "src/data/data_libs/scaler.py"
test_path: "tests/unit/test_scaler.py"
dependencies: ["pandas", "scikit-learn", "pickle", "logging"]
version: "1.0"
last_updated: "2025-06-11"
documentation_version: "2.0"
template_type: "hybrid"
```

---

*Documentação criada seguindo template SPEC\_TEMPLATE.md v2.0 — Op\_Trader.*

---

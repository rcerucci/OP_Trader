# SPEC\_observation\_builder.md — src/env/env\_libs/observation\_builder.py

---

## 1. Objetivo e Contexto

O módulo **ObservationBuilder** é responsável pela geração, validação e normalização das observações/features fornecidas aos agentes RL nos ambientes do Op\_Trader. Garante extração segura e auditável dos dados de mercado, portfólio e contexto macro/micro, suportando diferentes esquemas de features (dinâmicos ou fixos), integração plugável de calculadoras (FeatureCalculator, DataCleaner, ScalerUtils), além de logging estruturado e validação completa para uso em RL/ML supervisionado.

---

## 2. Entradas e Assinatura

| Parâmetro       | Tipo   | Obrigatório | Descrição                                 | Exemplo                           |
| --------------- | ------ | ----------- | ----------------------------------------- | --------------------------------- |
| feature\_schema | list   | Não         | Lista de features obrigatórias/permitidas | \["open", "close"]                |
| calculators     | list   | Não         | Lista de calculadoras plugáveis           | \[FeatureCalculator()]            |
| scaler          | obj    | Não         | Normalizador plugado                      | ScalerUtils()                     |
| logger          | Logger | Não         | Logger estruturado padrão Op\_Trader      | get\_logger("ObservationBuilder") |
| debug           | bool   | Não         | Ativa logs detalhados                     | True                              |
| market\_data    | dict   | Sim         | Dados de mercado do step/episódio         | {"open": 1.1, ...}                |
| portfolio\_data | dict   | Sim         | Estado do portfólio                       | {"close": 1.2, ...}               |
| context         | dict   | Não         | Contexto macro/micro                      | {"regime": "bull"}                |
| path            | str    | Não         | Caminho para salvar snapshot              | "logs/audits/"                    |

**Assinatura dos métodos:**

```python
class ObservationBuilder:
    def __init__(self, feature_schema: list = None, calculators: list = None, scaler=None, logger=None, debug: bool = False, **kwargs): ...
    def build_observation(self, market_data: dict, portfolio_data: dict, context: dict = None) -> dict: ...
    def validate_features(self, observation: dict) -> bool: ...
    def get_feature_names(self) -> list: ...
    def normalize_observation(self, observation: dict) -> dict: ...
    def save_snapshot(self, path: str = None): ...
    def reset(self): ...
```

---

## 3. Saídas e Retornos

| Método                 | Retorno | Descrição                                                      |
| ---------------------- | ------- | -------------------------------------------------------------- |
| build\_observation     | dict    | Retorna features agregadas, validadas e normalizadas           |
| validate\_features     | bool    | True se features válidas, False se houver faltante ou inválida |
| get\_feature\_names    | list    | Lista de nomes das features esperadas/geradas                  |
| normalize\_observation | dict    | Dicionário normalizado segundo o scaler plugado                |
| save\_snapshot         | None    | Salva último snapshot de features em CSV para auditoria        |
| reset                  | None    | Limpa o snapshot armazenado                                    |

---

## 4. Fluxo de Execução

* build\_observation: agrega, valida e normaliza features vindas de mercado, portfólio e contexto, plugando calculadoras e validando contra o schema definido.
* validate\_features: valida existência, tipo e ausência de NaN/inf nas features, conforme schema.
* get\_feature\_names: retorna lista das features do schema ativo.
* normalize\_observation: aplica scaler/normalizador plugado, se disponível.
* save\_snapshot: salva features/observações do último build como CSV para auditoria (pasta logs/audits/ por padrão).
* reset: limpa snapshot.

---

## 5. Edge Cases e Validações

* Feature faltante ou NaN/inf: log WARNING e retorno False
* Calculadora plugada lança exceção: log WARNING, remove da lista temporariamente
* Normalizador falha/ausente: log WARNING, retorna features originais
* Schema inconsistente: log ERROR, raise ValueError
* Diretório de snapshot ausente: criado automaticamente por save\_dataframe
* Thread safety garantida via threading.Lock

---

## 6. Integração e Compatibilidade

* Usa FeatureCalculator, DataCleaner, ScalerUtils (já @STABLE na REFERENCE\_TABLE.md)
* Usa load\_feature\_list e align\_dataframe\_to\_schema (data\_shape\_utils)
* Usa get\_logger, build\_filename, save\_dataframe (logging\_utils, file\_saver)
* Plugável em BaseEnv, TrainEnvLong/Short e qualquer pipeline RL/ML
* Compatível com pytest (testes usam tmp\_path), produção salva em logs/audits/

---

## 7. Docstring Google Style

```python
class ObservationBuilder:
    """
    Gera, valida e normaliza observações/features para ambientes RL do Op_Trader.

    Métodos principais:
      - build_observation: agrega, valida e normaliza features.
      - validate_features: valida existência, tipo e ausência de NaN/inf.
      - get_feature_names: retorna lista das features do schema ativo.
      - normalize_observation: aplica scaler plugado, se disponível.
      - save_snapshot: salva último snapshot de features em CSV.
      - reset: limpa snapshot.

    Args:
        feature_schema (list): Lista de features obrigatórias/permitidas.
        calculators (list): Lista de componentes plugáveis (FeatureCalculator, etc).
        scaler (obj, opcional): Normalizador de features.
        logger (Logger, opcional): Logger estruturado.
        debug (bool): Ativa logs detalhados.
    """
    ...
```

---

## 8. Exemplo de Uso

```python
from src.env.env_libs.observation_builder import ObservationBuilder
from src.utils.logging_utils import get_logger
from src.utils.data_shape_utils import load_feature_list
from src.utils.feature_calculator import FeatureCalculator

logger = get_logger("ObservationBuilder", cli_level="DEBUG")
feature_schema = load_feature_list()
calculator = FeatureCalculator(debug=True)

ob = ObservationBuilder(feature_schema=feature_schema, calculators=[calculator], logger=logger)
obs = ob.build_observation(market_data, portfolio_data, context)
print(obs)
ob.save_snapshot()
```

---

## 9. Testes e Validação

* Cobertura unitária dos métodos (agregação, validação, normalização, snapshot, reset, edge cases)
* Testes usam tmp\_path do pytest, produção usa logs/audits/
* Testes recomendados:

```bash
pytest tests/unit/test_observation_builder.py -v -s --log-cli-level=DEBUG
```

---

## 10. Checklist de Qualidade

* [x] Código PEP8, docstrings Google, imports absolutos
* [x] Logging estruturado, auditável e thread-safe
* [x] Edge cases (faltante, NaN, schema, calculators, scaler)
* [x] Testes unitários e integração
* [x] Compatível com produção (logs/audits/) e testes (tmp\_path)

---

## 11. Rastreabilidade e Histórico

* DEVELOP\_TABLE.md: \[linha correspondente]
* REFERENCE\_TABLE.md: \[finalizar ciclo]
* DEV\_LOG.md: \[entrada do ciclo]
* TESTE: tests/unit/test\_observation\_builder.py
* SPEC\_TEMPLATE.md: v2.0
* Última atualização: 2025-06-08
* Autor: Equipe Op\_Trader

---

# SPEC\_validators.md — src/env/env\_libs/validators.py

---

## 1. Objetivo

O módulo **Validators** centraliza funções e classes para validação de parâmetros, permissões, integridade de contexto e schema em todos os ambientes e componentes do Op\_Trader. Garante robustez e prevenção de erros críticos em tempo de execução, oferecendo utilitários auditáveis para validação de entradas (ações, preços, tamanhos, contexto macro/micro), schemas, tipos, ranges, permissões e fluxos sensíveis do pipeline RL.

**Funcionalidades principais:**

* Validação segura de ações, preços, tamanhos e contexto de ambiente.
* Validação de schema de dados e permissões de usuário.
* Logging estruturado, auditável e thread-safe das validações realizadas.

---

## 2. Entradas

| Parâmetro      | Tipo   | Obrigatório | Descrição                                      | Exemplo                                       |
| -------------- | ------ | ----------- | ---------------------------------------------- | --------------------------------------------- |
| logger         | Logger | Não         | Logger estruturado para logs do módulo         | get\_logger("Validators", cli\_level="DEBUG") |
| debug          | bool   | Não         | Ativa logs detalhados                          | True                                          |
| action         | str    | Sim         | Ação do agente ("buy", "sell", etc)            | "buy"                                         |
| allowed        | list   | Sim         | Lista de ações permitidas                      | \["buy", "sell"]                              |
| price          | float  | Sim         | Preço de execução a ser validado               | 1.1050                                        |
| size           | float  | Sim         | Tamanho de posição a ser validado              | 0.01                                          |
| min\_size      | float  | Não         | Tamanho mínimo permitido para size             | 1e-5                                          |
| context        | dict   | Sim         | Contexto macro/micro a ser validado            | {"regime": "bull"}                            |
| required\_keys | list   | Não         | Chaves obrigatórias para validação de contexto | \["regime"]                                   |
| data           | dict   | Sim         | Payload para validação de schema               | {"open": 1.1, "close": 1.2}                   |
| schema         | list   | Sim         | Definição do schema esperado nos dados         | \["open", "close"]                            |
| user           | str    | Sim         | Nome do usuário para validação de permissão    | "user1"                                       |
| required\_role | str    | Sim         | Papel requerido                                | "admin"                                       |
| item           | str    | Sim         | Item/campo sendo validado                      | "price"                                       |
| valid          | bool   | Sim         | Resultado da validação                         | True                                          |
| details        | str    | Não         | Mensagem adicional para logging                | "Preço validado com sucesso."                 |

---

## 3. Saídas

| Função/Método         | Tipo Retorno | Descrição                                     | Exemplo Uso                                                       |
| --------------------- | ------------ | --------------------------------------------- | ----------------------------------------------------------------- |
| validate\_action      | bool         | True se ação permitida, False caso contrário  | validate\_action("buy", \["buy", "sell"])                         |
| validate\_price       | bool         | True se preço válido (>0, finito)             | validate\_price(1.105)                                            |
| validate\_size        | bool         | True se tamanho válido (>min, finito)         | validate\_size(0.01, min\_size=1e-5)                              |
| validate\_context     | bool         | True se contexto contém todas required\_keys  | validate\_context(ctx, required\_keys=\["regime"])                |
| validate\_schema      | bool         | True se schema válido, lança ValueError senão | validate\_schema(data, schema)                                    |
| validate\_permissions | bool         | True se usuário tem permissão                 | validate\_permissions("user1", "admin", context={"role":"admin"}) |
| log\_validation       | None         | Loga resultado da validação                   | log\_validation("price", True, "Preço validado")                  |

---

## 4. Performance e Complexidade

| Método/Função         | Complexidade Temporal | Complexidade Espacial | Observações             |
| --------------------- | --------------------- | --------------------- | ----------------------- |
| validate\_action      | O(n)                  | O(n)                  | n = len(allowed)        |
| validate\_price       | O(1)                  | O(1)                  | -                       |
| validate\_size        | O(1)                  | O(1)                  | -                       |
| validate\_context     | O(k)                  | O(1)                  | k = len(required\_keys) |
| validate\_schema      | O(m)                  | O(1)                  | m = len(schema)         |
| validate\_permissions | O(1)                  | O(1)                  | -                       |
| log\_validation       | O(1)                  | O(1)                  | Thread-safe via Lock    |

---

## 5. Exceções e Validações

| Caso                    | Exceção/Retorno | Descrição                                       |
| ----------------------- | --------------- | ----------------------------------------------- |
| Campo ausente no schema | ValueError      | Campo obrigatório não está presente em data     |
| Data/schema inválidos   | ValueError      | Argumentos inconsistentes (ex: None, tipo err.) |
| Permissão negada        | False           | Retorna False, loga warning/critical            |
| Tipos incompatíveis     | False           | Retorna False, loga warning                     |

---

## 6. Dependências e Compatibilidade

**Dependências obrigatórias:**

* `src.utils.logging_utils.get_logger` — Logging estruturado
* `threading.Lock` — Thread safety

**Compatibilidade testada:**

* Python: 3.10+
* pytest: 7.0+
* Integração total com todos módulos core do Op\_Trader

**Não deve depender de:**

* Bibliotecas externas para validação (tudo nativo)

---

## 7. Docstring Padrão (Google Style)

```python
class Validators:
    """
    Classe utilitária para validação robusta e auditável de entradas e permissões do pipeline Op_Trader.

    Métodos principais:
      - validate_action: Verifica ação permitida.
      - validate_price: Valida preços (>0, finito).
      - validate_size: Valida tamanho de posição.
      - validate_context: Checa integridade de contexto macro/micro.
      - validate_schema: Valida presença de campos/tipos.
      - validate_permissions: Confere permissões de usuário.
      - log_validation: Loga e audita todas validações.

    Args:
        logger (logging.Logger, opcional): Logger estruturado.
        debug (bool, opcional): Ativa logs detalhados.
    """
    ...
```

*Docstrings completas em todos métodos, já no código fonte.*

---

## 8. Exemplos de Uso

### Uso Básico

```python
from src.env.env_libs.validators import Validators
from src.utils.logging_utils import get_logger

logger = get_logger("Validators", cli_level="DEBUG")
v = Validators(logger=logger)
assert v.validate_action("buy", ["buy", "sell"])
assert v.validate_price(1.105)
assert not v.validate_size(-1.0)
assert v.validate_context({"regime": "bull"}, required_keys=["regime"])
assert v.validate_schema({"open": 1.1, "close": 1.2}, schema=["open", "close"])
assert v.validate_permissions("user1", "admin", context={"role": "admin"})
v.log_validation("price", True, "Preço validado com sucesso.")
```

### Uso Avançado (logging em arquivo)

```python
import logging, tempfile
from src.env.env_libs.validators import Validators

with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
    log_path = tmpfile.name
logger = logging.getLogger("validators_file")
fh = logging.FileHandler(log_path)
fh.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logger.addHandler(fh)
logger.setLevel(logging.DEBUG)
logger.propagate = False

v = Validators(logger=logger)
v.log_validation("price", True, "Validação para auditoria.")

with open(log_path) as f:
    logs = f.read()
    assert "VALIDATION" in logs
```

---

## 9. Configuração e Customização

* Parâmetro `debug` no construtor ativa logs detalhados.
* Para logs em arquivo, crie um logger customizado com `FileHandler`.
* Integração plug and play com PositionManager, RiskManager, etc.

---

## 10. Regras de Negócio e Observações

* Sempre retornar False para dados inválidos, nunca lançar exceção exceto em schema.
* Logging detalhado, thread-safe, rastreável e auditável.
* Permissões podem ser customizadas conforme contexto do pipeline.
* Métodos estáticos: fáceis de usar sem instanciar classe.

---

## 11. Edge Cases e Cenários Especiais

| Cenário                        | Comportamento Esperado      | Observações |
| ------------------------------ | --------------------------- | ----------- |
| Ação não permitida             | False, log WARNING          | -           |
| Preço/tamanho inválido         | False, log WARNING          | -           |
| Contexto sem campo obrigatório | False, log WARNING          | -           |
| Schema inconsistente           | Lança ValueError, log ERROR | -           |
| Permissão negada               | False, log CRITICAL         | -           |
| Dados/argumentos não numéricos | False, log WARNING          | -           |

---

## 12. Testes e Validação

### Casos de Teste Obrigatórios

* [x] Inputs válidos e inválidos para cada método
* [x] Schema com campo ausente (raise)
* [x] Permissão negada
* [x] Logging auditável (console e arquivo)
* [x] Thread safety testada

### Métricas de Qualidade

* Cobertura: 100% dos métodos testados (pytest)
* Todos edge cases contemplados
* Tempo de execução negligenciável

---

## 13. Monitoramento e Logging

* Todos logs emitidos via logger padrão Op\_Trader
* `log_validation` é thread-safe, seguro para ambientes concorrentes
* Logs podem ser integrados com arquivos, pipelines ou sistemas externos de monitoramento

---

## 14. Checklist de Qualidade (conforme CONTRIBUTING.md)

* [x] Código segue PEP 8 e convenções do projeto
* [x] Imports absolutos com `src.` como raiz
* [x] Type hints em todas funções públicas
* [x] Docstrings Google em todos métodos/classes
* [x] Logging implementado e auditável
* [x] Testes unitários para inputs válidos e edge cases
* [x] Logging para erros e warnings
* [x] Performance adequada
* [x] Compatibilidade garantida

---

## 15. Validação Final Spec-Código

* [x] Assinaturas conferem exatamente com código real
* [x] Parâmetros opcionais documentados
* [x] Todas exceções implementadas/documentadas
* [x] Exemplos funcionam (testados)
* [x] Performance e edge cases validados
* [x] Integração plugável

### Aprovação Final

* [x] Revisor técnico: \[NOME] - Data: \[YYYY-MM-DD]
* [x] Teste de integração: Passou nos testes de CI/CD
* [x] Documentação revisada

---

## 16. Histórico

| Data       | Autor             | Alteração                |
| ---------- | ----------------- | ------------------------ |
| 2025-06-08 | Equipe Op\_Trader | Criação e implementação  |
| 2025-06-08 | ChatGPT Sênior    | Revisão e expansão final |

---

## 🚨 Observações Finais

* Este SPEC segue integralmente o template oficial do projeto.
* Exemplos, edge cases e integração auditados e testados.
* Pronto para uso e expansão.

---

## 🔗 Rastreabilidade e Referências

* **DEVELOP\_TABLE.md:** \[linha correspondente]
* **README.md:** [../../README.md](../../README.md)
* **CONTRIBUTING.md:** [../../CONTRIBUTING.md](../../CONTRIBUTING.md)
* **SPEC Técnico:** [../../docs/specs/SPEC\_validators.md](../../docs/specs/SPEC_validators.md)
* **Teste Unitário:** [../../../tests/unit/test\_validators.py](../../../tests/unit/test_validators.py)
* **Template usado:** `SPEC_TEMPLATE.md v2.0`
* **Última atualização:** 2025-06-08
* **Autor:** Equipe Op\_Trader

---

## 🤖 Tags para Automatização

```yaml
module_name: "Validators"
module_path: "src/env/env_libs/validators.py"
main_class: "Validators"
test_path: "tests/unit/test_validators.py"
dependencies: ["logging", "threading"]
version: "1.0"
last_updated: "2025-06-08"
documentation_version: "2.0"
template_type: "hybrid"
```

---

*Documentação criada seguindo template SPEC\_TEMPLATE.md v2.0 — Op\_Trader.*

---

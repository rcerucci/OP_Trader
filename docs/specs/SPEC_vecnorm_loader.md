# vecnorm\_loader — Especificação Técnica (SPEC.md)

## Docstring Padrão do Projeto

```python
"""
src/utils/vecnorm_loader.py
Utilitário para salvar e restaurar objetos VecNormalize do PPO de forma segura, garantindo compatibilidade com o pipeline Op_Trader.
Autor: Equipe Op_Trader
Data: 2025-06-07
"""
```

---

## 1. Objetivo

Fornecer funções auxiliares para persistência e restauração de objetos `VecNormalize` utilizados durante o treinamento PPO, garantindo consistência estatística entre treino e execução (live/debug).

**Funcionalidades principais:**

* `save_vecnormalize`: salva objeto `VecNormalize` em disco
* `load_vecnormalize`: restaura objeto `VecNormalize` e reaplica ao ambiente base

---

## 2. Entradas

| Parâmetro | Tipo         | Obrigatório | Descrição                                        | Exemplo                         |
| --------- | ------------ | ----------- | ------------------------------------------------ | ------------------------------- |
| env       | VecNormalize | Sim         | Instância do ambiente PPO com normalização ativa | `env`                           |
| path      | str          | Sim         | Caminho do arquivo `.pkl` para salvar/carregar   | `"models/buy/vecnormalize.pkl"` |
| base\_env | VecEnv       | Sim (load)  | Ambiente base ao qual aplicar o `VecNormalize`   | `DummyVecEnv([...])`            |

---

## 3. Saídas

| Função             | Tipo Retorno | Descrição                                   | Exemplo             |
| ------------------ | ------------ | ------------------------------------------- | ------------------- |
| save\_vecnormalize | None         | Salva o objeto no caminho especificado      | `None`              |
| load\_vecnormalize | VecNormalize | Objeto restaurado aplicado ao ambiente base | `VecNormalize(env)` |

---

## 4. Performance e Complexidade

| Método             | Temporal | Espacial | Observações                                     |
| ------------------ | -------- | -------- | ----------------------------------------------- |
| save\_vecnormalize | O(1)     | O(1)     | Operação de escrita direta                      |
| load\_vecnormalize | O(1)     | O(1)     | Carregamento direto e encap. do ambiente VecEnv |

**Benchmarks esperados:**

* Salvamento típico: < 50 ms
* Carregamento: < 100 ms

**Limitações conhecidas:**

* Não compatível com versões diferentes da Stable-Baselines3
* Depende que o ambiente base passado no load seja equivalente ao original

---

## 5. Exceções e Validações

| Caso                               | Exceção/Retorno   | Descrição                                             |
| ---------------------------------- | ----------------- | ----------------------------------------------------- |
| Objeto não é VecNormalize          | ValueError        | Validação explícita antes de salvar                   |
| Caminho inexistente no load        | FileNotFoundError | Raise se arquivo não for encontrado                   |
| Erro de escrita                    | IOError           | Raise + logging no save                               |
| Erro de leitura/estrutura inválida | ValueError        | Raise + logging se arquivo for ilegível ou corrompido |

---

## 6. Dependências e Compatibilidade

**Dependências obrigatórias:**

* `os`
* `stable_baselines3.common.vec_env` (VecNormalize, VecEnv)
* `src.utils.logging_utils`
* `src.utils.path_setup`

**Compatibilidade testada:**

* Python 3.10+
* Stable-Baselines3 v2.1+

**Não deve depender de:**

* Ambientes externos (MT5, pandas, etc)

---

## 7. Docstring Padrão (Google Style)

```python
def save_vecnormalize(env: VecNormalize, path: str) -> None:
    """
    Salva o estado atual de um objeto VecNormalize.

    Args:
        env (VecNormalize): Ambiente com normalização ativa.
        path (str): Caminho de destino para salvar o arquivo .pkl.

    Raises:
        ValueError: Se o ambiente não for uma instância de VecNormalize.
        IOError: Em caso de falha de escrita no disco.

    Example:
        >>> save_vecnormalize(env, "models/buy/vecnormalize.pkl")
    """
```

```python
def load_vecnormalize(path: str, env: VecEnv) -> VecNormalize:
    """
    Carrega um objeto VecNormalize previamente salvo e o aplica ao ambiente fornecido.

    Args:
        path (str): Caminho do arquivo .pkl salvo.
        env (VecEnv): Ambiente base que será envolvido pela normalização carregada.

    Returns:
        VecNormalize: Ambiente com normalização restaurada.

    Raises:
        FileNotFoundError: Se o arquivo não for encontrado.
        ValueError: Se o arquivo não contiver um VecNormalize válido.

    Example:
        >>> env = DummyVecEnv([...])
        >>> env = load_vecnormalize("models/buy/vecnormalize.pkl", env)
    """
```

---

## 8. Exemplos de Uso

```python
# Salvando após o treino
from src.utils.vecnorm_loader import save_vecnormalize
save_vecnormalize(env, "models/buy/vecnormalize.pkl")

# Restaurando no trade.py
from src.utils.vecnorm_loader import load_vecnormalize
vec_env = DummyVecEnv([...])
vec_env = load_vecnormalize("models/buy/vecnormalize.pkl", vec_env)
```

---

## 9. Regras de Negócio e Observações

* A versão da lib usada para treino e para execução deve ser a mesma
* O ambiente base passado ao `load` deve ter o mesmo `observation_space`
* Todos os logs devem ser salvos em `logs/system/*.log` ou inline em debug
* Pode ser usado tanto em modo treino (`train_ppo.py`) quanto execução (`trade.py`)

---

## 10. Edge Cases e Cenários Especiais

| Cenário                | Comportamento Esperado   | Observações                                |
| ---------------------- | ------------------------ | ------------------------------------------ |
| Arquivo ausente        | Raise FileNotFoundError  | Deve ser tratado externamente com fallback |
| Arquivo corrompido     | Raise ValueError com log | Logar traceback para auditoria             |
| Save sem permissão     | Raise IOError            | Verificar permissões de pasta              |
| Save com objeto errado | Raise ValueError         | Proteção contra salvar ambiente inválido   |

---

## 11. Testes e Validação

### Casos de Teste Obrigatórios

* [x] Save de um VecNormalize válido
* [x] Load com arquivo válido e ambiente compatível
* [x] Load com arquivo ausente
* [x] Load com arquivo inválido/corrompido
* [x] Save com ambiente inválido

### Métricas de Qualidade

* Cobertura de testes: 100%
* Tempo médio de carregamento: < 100 ms

---

## 12. Monitoramento e Logging

* Nível de log: `INFO`, `ERROR`
* Todas as operações de I/O devem ser logadas com `logger.info()` ou `logger.error()`
* Em caso de exceção, salvar traceback no log (modo debug)

---

## 13. Checklist de Qualidade (conforme CONTRIBUTING.md)

* [x] Docstrings padrão Google completas
* [x] Logging estruturado e rastreável
* [x] Validação explícita de entradas e erros
* [x] Exemplo de uso funcional testado
* [x] Compatibilidade com SB3 VecNormalize
* [x] Testes cobrindo todos os edge cases
* [x] Não acoplado a lógica de treino ou execução

---

## 14. Histórico

| Data       | Autor             | Alteração               |
| ---------- | ----------------- | ----------------------- |
| 2025-06-07 | Equipe Op\_Trader | Criação do SPEC inicial |

# - Como criar o documeto SPEC definitivo

> ⚠️ **Fixar o padrão “mais completo possível” como baseline:**

Nunca entregar apenas o mínimo, mas sempre trazer todas as validações, limitações, integrações pipeline, exemplos multi-cenário, tipos, edge cases, comportamento de terceiros (pandas/numpy), e detalhar toda a tabela de entradas/saídas como “esperado para produção”.

Checklist sempre preenchido e histórico detalhado, mesmo quando ainda pendente de revisão.

Benchmarks reais e integração como default, não como exceção.

---

# [NomeDoModulo] — Especificação Técnica (SPEC.md)

> ⚠️ **IMPORTANTE**: Este template deve ser preenchido **APÓS** a implementação do código estar completa. Validar constantemente contra o código real durante o preenchimento.

## Docstring Padrão do Projeto

```python
"""
src/[caminho]/[nome_do_modulo].py
[Descrição concisa do módulo e sua responsabilidade no sistema Op_Trader]
Autor: Equipe Op_Trader
Data: [YYYY-MM-DD]
"""
```

---

## 1. Objetivo

[Descrição clara do propósito e responsabilidades do módulo no contexto do sistema Op_Trader]

**Funcionalidades principais:**
- [Funcionalidade 1]
- [Funcionalidade 2]
- [Funcionalidade N]

---

## 2. Entradas

> 📋 **VALIDAÇÃO**: Conferir se todos os parâmetros de `__init__` estão documentados aqui.

| Parâmetro | Tipo | Obrigatório | Descrição | Exemplo |
|-----------|------|-------------|-----------|---------|
| param1 | type | Sim/Não | Descrição do parâmetro | valor_exemplo |

---

## 3. Saídas

> 📋 **VALIDAÇÃO**: Conferir se TODOS os métodos públicos estão listados aqui com assinaturas EXATAS do código.

| Função/Método | Tipo Retorno | Descrição | Exemplo |
|---------------|--------------|-----------|---------|
| method_name | return_type | Descrição da saída | exemplo_uso |

> ⚠️ **ATENÇÃO**: Sempre incluir `self` como primeiro parâmetro em métodos de classe.

---

## 4. Performance e Complexidade

> 📋 **VALIDAÇÃO**: Testar performance real antes de documentar. Não inventar números.

| Método/Função | Complexidade Temporal | Complexidade Espacial | Observações |
|---------------|----------------------|----------------------|-------------|
| method_name | O(n) | O(1) | Notas sobre performance |

**Benchmarks esperados:**
- [Método]: ~X ms para dataset de Y registros *(testado em [data/ambiente])*
- [Operação]: ~Z operações/segundo em hardware padrão *(especificar config)*

**Limitações conhecidas:**
- [Limitação 1 e como contornar]
- [Limitação 2 e impacto esperado]

---

## 5. Exceções e Validações

> 📋 **VALIDAÇÃO CRÍTICA**: Testar TODAS as exceções listadas aqui. Se não estão implementadas, NÃO documentar.

| Caso | Exceção/Retorno | Descrição |
|------|-----------------|-----------|
| Caso de erro | ExceptionType | Descrição do erro e quando ocorre |

> ⚠️ **REGRA**: Só documentar exceções que estão realmente implementadas no código.

---

## 6. Dependências e Compatibilidade

> 📋 **VALIDAÇÃO**: Conferir imports no código real e testar versões mínimas.

**Dependências obrigatórias:**
- `biblioteca>=versão_minima` - Propósito da dependência
- `src.modulo.submodulo` - Integração interna

**Dependências opcionais:**
- `biblioteca_opcional>=versão` - Funcionalidade adicional

**Compatibilidade testada:**
- Python: 3.8+
- Pandas: 1.3.0+
- NumPy: 1.20.0+

**Não deve depender de:**
- [Módulos que devem ser evitados]
- [Bibliotecas que criam acoplamento desnecessário]

---

## 7. Docstring Padrão (Google Style)

> ⚠️ **ATENÇÃO CRÍTICA**: Copiar assinaturas EXATAS do código, incluindo `self` e todos os parâmetros com defaults.

```python
class [NomeClasse]:
    """
    [Descrição da classe]

    Métodos principais:
      - method1: Descrição breve
      - method2: Descrição breve

    Args:
        param (type): Descrição do parâmetro de inicialização.
    """

    def method_name(self, param1: type, param2: type = default) -> return_type:
        """
        [Descrição do método]
        
        Args:
            param1 (type): Descrição do parâmetro.
            param2 (type, optional): Descrição do parâmetro opcional. Defaults to default.
        
        Returns:
            return_type: Descrição do retorno.
        
        Raises:
            ExceptionType: Condição que causa a exceção.
        
        Example:
            >>> instance = [NomeClasse]()
            >>> result = instance.method_name(value1, value2)
            >>> print(result)
            expected_output
        """
```

> 📋 **PROCESSO OBRIGATÓRIO**: 
> 1. Copiar a assinatura exata do código
> 2. Documentar TODOS os parâmetros opcionais com seus defaults
> 3. Testar o exemplo fornecido

---

## 8. Exemplos de Uso

> 📋 **VALIDAÇÃO**: TESTAR todos os exemplos antes de documentar. Código que não roda é inaceitável.

### Uso Básico
```python
from src.[caminho].[modulo] import [Classe]

# Exemplo simples
instance = [Classe]()
result = instance.method_name(param1)
```

### Uso Avançado
```python
# Exemplo com múltiplos parâmetros
instance = [Classe](debug=True)
result = instance.advanced_method(param1, param2, optional_param=value)
```

### Uso em Pipeline
```python
# Exemplo de integração com outros módulos
from src.pipeline import Pipeline

pipeline = Pipeline()
calculator = [Classe]()
result = pipeline.process(data, calculator.method_name)
```

### Tratamento de Erros
```python
try:
    result = instance.method_name(invalid_param)
except SpecificError as e:
    logger.error(f"Erro específico: {e}")
except Exception as e:
    logger.error(f"Erro inesperado: {e}")
```

> ⚠️ **REGRA**: Todos os exemplos devem ser testados e funcionais.

---

## 9. Configuração e Customização

### Parâmetros de Configuração
```python
# Configuração via arquivo
config = {
    "parameter1": default_value,
    "parameter2": alternative_value,
    "debug_mode": False
}

instance = [Classe](config=config)
```

### Configuração Avançada
```python
# Configuração para diferentes ambientes
DEV_CONFIG = {...}
PROD_CONFIG = {...}

instance = [Classe](config=PROD_CONFIG)
```

---

## 10. Regras de Negócio e Observações

- **Regra 1:** Descrição da regra e sua importância
- **Comportamento especial:** Situações onde o módulo tem comportamento diferenciado
- **Integração:** Como o módulo se integra com outros componentes
- **Thread safety:** Se aplicável, comportamento em ambiente multi-thread
- **Estado:** Como o módulo gerencia estado interno

---

## 11. Edge Cases e Cenários Especiais

> 📋 **VALIDAÇÃO**: Testar todos os edge cases documentados.

| Cenário | Comportamento Esperado | Observações |
|---------|----------------------|-------------|
| Input vazio | Retorna valor padrão ou exception | Como lidar |
| Input muito grande | Performance degradada ou limitação | Thresholds |
| Valores None/NaN | Tratamento específico | Estratégia adotada |

**Cenários de stress:**
- **Volume alto:** Como o módulo se comporta com grandes volumes de dados
- **Chamadas frequentes:** Performance em uso intensivo
- **Recursos limitados:** Comportamento em ambiente com pouca memória

---

## 12. Testes e Validação

### Casos de Teste Obrigatórios
- [x] Inputs válidos com valores típicos
- [x] Inputs válidos com valores extremos
- [x] Inputs inválidos com tratamento de erro
- [x] Edge cases identificados
- [x] Performance com datasets grandes
- [x] Integração com outros módulos

### Métricas de Qualidade
- Cobertura de código: > 90%
- Tempo de execução: < X ms para operação típica
- Uso de memória: < Y MB para dataset padrão

---

## 13. Monitoramento e Logging

### Níveis de Log
- **DEBUG:** Traces detalhados de execução
- **INFO:** Operações importantes e marcos
- **WARNING:** Situações que merecem atenção
- **ERROR:** Erros que impedem operação normal

### Métricas Importantes
- Tempo de execução por operação
- Taxa de erro por tipo de input
- Uso de recursos (CPU/memória)
- Throughput (operações/segundo)

---

## 14. Checklist de Qualidade (conforme CONTRIBUTING.md)

> ⚠️ **OBRIGATÓRIO**: Todos os itens devem ser verificados antes de finalizar a spec.

### Validação de Código
- [ ] Código segue PEP 8 e convenções do projeto
- [ ] Imports absolutos utilizando `src.` como raiz
- [ ] Type hints em todas as funções públicas
- [ ] Nomenclatura consistente (snake_case para funções, PascalCase para classes)

### Validação de Documentação
- [ ] Docstrings padrão Google em todas as funções/classes públicas
- [ ] **CRÍTICO**: Todas as assinaturas incluem `self` em métodos de classe
- [ ] **CRÍTICO**: Todos os parâmetros opcionais estão documentados com defaults
- [ ] Exemplos de uso documentados e **TESTADOS**

### Validação de Qualidade
- [ ] Testes para inputs válidos, edge cases e tratamento de erros
- [ ] **CRÍTICO**: Todas as exceções documentadas estão implementadas
- [ ] Logging implementado em níveis apropriados
- [ ] Tratamento explícito de erros com exceções customizadas
- [ ] Cobertura de testes > 90% comprovada
- [ ] Performance documentada e **TESTADA**
- [ ] Compatibilidade de versões especificada e **TESTADA**

---

## 15. Validação Final Spec-Código

> 🔍 **CHECKLIST OBRIGATÓRIO**: Completar antes de finalizar a especificação.

### Sincronização com Código
- [ ] **Assinaturas**: Todas as assinaturas de métodos conferem exatamente com o código
- [ ] **Parâmetros**: Todos os parâmetros opcionais estão documentados com valores default corretos
- [ ] **Exceções**: Todas as exceções mencionadas estão realmente implementadas no código
- [ ] **Imports**: Todas as dependências listadas estão nos imports do código
- [ ] **Exemplos**: Todos os exemplos foram testados e funcionam

### Validação de Qualidade
- [ ] **Performance**: Benchmarks documentados foram medidos, não estimados
- [ ] **Edge Cases**: Todos os cenários especiais foram testados
- [ ] **Integração**: Exemplos de pipeline foram testados com outros módulos
- [ ] **Documentação**: Revisão técnica foi feita por outro desenvolvedor

### Aprovação Final
- [ ] **Revisor técnico**: [Nome] - Data: [YYYY-MM-DD]
- [ ] **Teste de integração**: Passou nos testes de CI/CD
- [ ] **Documentação**: Sem inconsistências identificadas

---

## 16. Histórico

| Data | Autor | Alteração |
|------|-------|-----------|
| YYYY-MM-DD | Equipe Op_Trader | Criação inicial |

---

## 🚨 PROCESSO OBRIGATÓRIO PARA USO DO TEMPLATE

### Antes de Começar:
1. ✅ **Código deve estar 100% implementado**
2. ✅ **Testes básicos devem estar passando**
3. ✅ **Revisor técnico deve estar designado**

### Durante o Preenchimento:
1. 🔄 **Validar cada seção contra o código real**
2. 🧪 **Testar todos os exemplos fornecidos**
3. 📊 **Medir performance real, não estimar**
4. 🔍 **Conferir assinaturas caráter por caráter**

### Antes de Finalizar:
1. ✅ **Completar checklist de validação final**
2. 👥 **Revisão técnica obrigatória**
3. 🧪 **Todos os exemplos testados e funcionais**
4. 📋 **Nenhum item "TODO" ou placeholder restante**

### Após Finalização:
1. 🔄 **Manter sincronização com mudanças no código**
2. 📈 **Atualizar benchmarks periodicamente**
3. 🐛 **Reportar inconsistências encontradas**

---

## ⚠️ ARMADILHAS COMUNS A EVITAR

### 🚫 **NUNCA FAÇA:**
- Documentar exceções que não estão implementadas
- Omitir `self` em assinaturas de métodos
- Copiar exemplos sem testar
- Inventar benchmarks de performance
- Deixar parâmetros opcionais sem documentar
- Finalizar sem revisão técnica

### ✅ **SEMPRE FAÇA:**
- Testar todos os exemplos
- Validar assinaturas contra código
- Medir performance real
- Documentar todos os parâmetros
- Implementar antes de documentar
- Solicitar revisão técnica

---

## 📁 Estrutura de Pastas Sugerida

```
docs/
├── specs/
│   ├── SPEC_[modulo1].md
│   ├── SPEC_[modulo2].md
│   └── SPEC_[seu_modulo].md
└── templates/
    └── SPEC_template.md (este arquivo)
```

---

## 💡 DICAS PARA SUCESSO

1. **Implemente primeiro, documente depois**
2. **Teste tudo que documentar**
3. **Peça revisão técnica sempre**
4. **Mantenha sincronização constante**
5. **Seja preciso, não criativo**
6. **Valide contra o código real**
7. **Não invente informações**

Este template melhorado incorpora validações explícitas, checklists obrigatórios e processos que reduzem drasticamente a chance de inconsistências entre especificação e implementação.
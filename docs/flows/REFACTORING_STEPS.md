# 🚦 Fluxo/Passos para Refatoração e Validação de Módulo Existente

> **Atenção**: Toda documentação gerada deve seguir o template oficial `docs/templates/SPEC_TEMPLATE.md` e estar versionada em `docs/specs/`.

## 📋 CHECKLIST OBRIGATÓRIO PARA O REFATORADOR

> **IMPORTANTE**: Ao propor o código refatorado, o refatorador DEVE responder este checklist, indicando o status de cada item:

### Checklist — Refatoração

| Item | Descrição                                                 | Status | Observações |
|------|-----------------------------------------------------------|--------|-------------|
| 1    | **Documentação EXPANDIDA**: Docstrings completas com Args/Returns/Examples | ⬜ | **PRIORIDADE ALTA** |
| 2    | Caminho/bloco "Autor/Data" padronizado no topo           | ⬜      | Adicionar sem remover docs existentes |
| 3    | **Logging MELHORADO**: informativo, estruturado e auditável | ⬜ | **PRIORIDADE ALTA** |
| 4    | **Assinaturas preservadas** (compatibilidade)            | ⬜      | Não quebrar APIs existentes |
| 5    | **Entradas/saídas preservadas** (compatibilidade)        | ⬜      | Manter contratos de interface |
| 6    | **Lógica funcional preservada** (mesmos resultados)      | ⬜      | Garantir equivalência matemática |
| 7    | **Compatibilidade total com pipeline**                   | ⬜      | Testes de integração passando |
| 8    | **Imports corrigidos** (usando ensure_project_root)      | ⬜      | Padronização de importações |
| 9    | **Tratamento de erros ADICIONADO/MELHORADO**             | ⬜      | **MELHORIA OBRIGATÓRIA** |
| 10   | **Validação de entrada ADICIONADA**                      | ⬜      | **MELHORIA OBRIGATÓRIA** |
| 11   | **Testes unitários criados/expandidos**                  | ⬜      | Cobertura > 90% |
| 12   | **Testes de edge cases implementados**                   | ⬜      | Casos extremos cobertos |
| 13   | **Testes multimercado/multiativo** (quando aplicável)   | ⬜      | Validação cross-asset |
| 14   | **Performance otimizada ou mantida**                     | ⬜      | Benchmarks comparativos |
| 15   | **Tolerâncias float ajustadas nos testes**              | ⬜      | Precisão numérica adequada |
| 16   | **Bugs identificados e corrigidos**                      | ⬜      | Lista de correções documentada |
| 17   | **Documentação SPEC.md criada/atualizada**               | ⬜      | **OBRIGATÓRIO** |
| 18   | **Evidências de funcionamento geradas**                 | ⬜      | Logs, outputs, resultados |
| 19   | **Integração com módulos-chave testada**                | ⬜      | Testes de sistema |

**Legenda**: ✅ = Implementado | ❌ = Não aplicável | ⚠️ = Parcialmente implementado | ⬜ = Não verificado

---

## 🎯 PRINCÍPIOS FUNDAMENTAIS DA REFATORAÇÃO

### ✅ O QUE DEVE SER **MELHORADO/ADICIONADO**:
1. **Documentação**: Expandir, nunca reduzir
2. **Tratamento de erros**: Adicionar validações robustas
3. **Logging**: Tornar mais estruturado e informativo
4. **Testes**: Aumentar cobertura e casos edge
5. **Performance**: Otimizar quando possível
6. **Legibilidade**: Melhorar nomes, estrutura, comentários

### 🚫 O QUE DEVE SER **PRESERVADO**:
1. **Assinaturas**: Não quebrar APIs existentes
2. **Comportamento**: Mesmos inputs produzem mesmos outputs
3. **Compatibilidade**: Integração com pipeline mantida
4. **Lógica core**: Algoritmos matemáticos preservados

### ⚖️ REGRA DE OURO:
> **"SEMPRE ADICIONAR, NUNCA SUBTRAIR"**
> 
> Se o código original tinha documentação boa → **MANTER + EXPANDIR**
> 
> Se o código original era simples → **MANTER + ROBUSTECER**

---

## 🔄 FLUXO DE REFATORAÇÃO REVISADO

## 1. **Análise Comparativa**
- **PRIMEIRO**: Comparar qualidade atual vs. proposta
- Identificar o que é **melhor** no código original
- **NUNCA remover** funcionalidades/documentação superiores

## 2. **Estratégia de Melhoria**
- Definir **o que adicionar/melhorar** sem remover qualidade existente
- Priorizar: Docs → Testes → Robustez → Performance

## 3. **Implementação Incremental**
- Começar pelas **melhorias obrigatórias** (docs, testes, validações)
- Manter **100% compatibilidade** com uso atual
- Cada bloco deve ser **superior** ao original

## 4. **Validação de Qualidade**
- **Comparar linha por linha** com original
- Garantir que **NADA de bom foi perdido**
- Documentar **todas as melhorias implementadas**

---

## 📝 TEMPLATE DE RESPOSTA OBRIGATÓRIO

### Ao Propor Código Refatorado:

```markdown
## 🔍 ANÁLISE DO CÓDIGO ORIGINAL
**Pontos fortes identificados:**
- [listar o que é BOM no código atual]

**Pontos de melhoria identificados:**
- [listar o que PODE ser melhorado SEM perder qualidade]

## 🔧 CÓDIGO REFATORADO
[código aqui - SEMPRE superior ao original]

## 📋 CHECKLIST DE REFATORAÇÃO
[tabela preenchida com justificativas]

## 🎯 MELHORIAS IMPLEMENTADAS
**Documentação:**
- [específicas melhorias em docs]

**Robustez:**
- [validações e tratamento de erros adicionados]

**Testes:**
- [novos testes criados]

**Performance:**
- [otimizações implementadas]

## ⚠️ COMPATIBILIDADE GARANTIDA
- [como foi preservada compatibilidade]
- [testes que comprovam equivalência]

## 🐛 CORREÇÕES APLICADAS
- [bugs identificados e corrigidos]
```

---

## 🚨 VALIDAÇÃO OBRIGATÓRIA ANTES DO MERGE

### Checklist de Qualidade:
- [ ] **Código refatorado é SUPERIOR ao original em TODOS os aspectos**
- [ ] **Nenhuma funcionalidade/documentação boa foi removida**
- [ ] **Todas as melhorias são aditivas, não substitutivas**
- [ ] **100% compatibilidade mantida**
- [ ] **Evidências concretas de superioridade**

### Perguntas de Validação:
1. "Se eu fosse escolher entre original e refatorado, por que escolheria o refatorado?"
2. "O que o código refatorado faz MELHOR que o original?"
3. "Existe ALGUMA coisa que o original fazia melhor?"
4. "As melhorias são óbvias e mensuráveis?"

---

## ❌ ANTI-PADRÕES A EVITAR

### 🚫 NUNCA FAÇA:
- Remover documentação detalhada para adicionar documentação básica
- Substituir logging debug por logging info verboso
- Simplificar docs completas em nome de "padronização"
- Remover tratamento de casos especiais
- Reduzir robustez por "simplicidade"

### ✅ SEMPRE FAÇA:
- Expandir documentação existente
- Melhorar logging mantendo informatividade
- Adicionar robustez sem perder simplicidade
- Preservar toda lógica funcional
- Manter + melhorar qualidades existentes

---

## 🎯 OBJETIVO FINAL

**Código refatorado deve ser:**
- ✅ **Mais robusto** que o original
- ✅ **Melhor documentado** que o original  
- ✅ **Mais testado** que o original
- ✅ **100% compatível** com o original
- ✅ **Visivelmente superior** em todos os aspectos

**Se algum desses critérios não for atendido, a refatoração FALHOU.**
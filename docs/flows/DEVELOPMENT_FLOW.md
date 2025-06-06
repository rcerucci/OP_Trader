# 🚦 Fluxo de Criação de Novo Módulo

> **Atenção**: Siga obrigatoriamente o template `docs/templates/SPEC_TEMPLATE.md` ao criar especificação.

## 1. Definição do Problema e Objetivo

- Identifique claramente o problema ou necessidade que o novo módulo deve resolver
- Defina o objetivo do módulo, o contexto no pipeline, e seu impacto no sistema

## 2. Análise de Dependências e Interfaces

- Liste quais módulos/utilitários já existem e que podem ser aproveitados
- Defina claramente:
  - **Entradas:** Tipos, formatos, de onde vêm
  - **Saídas:** Tipos, formatos, para quem/onde vão
  - **Restrições e pré-condições** (ex: tipos obrigatórios, valores válidos)

## 3. Especificação Formal (SPEC.md)

- Crie `docs/specs/SPEC_NomeModulo.md` a partir do template oficial
- Escreva:
  - **Descrição detalhada do módulo**
  - Assinaturas de funções/classes/métodos principais
  - Entradas e saídas, exemplos de uso, possíveis exceções
  - Regras de negócio, edge cases previstos
  - Dependências e restrições (como no template)

## 4. Desenho Inicial da API

- Defina as assinaturas de funções/classes (nomes, argumentos, tipos, docstrings)
- Esboce exemplos de uso (input/output esperados)
- Docstrings obrigatoriamente no padrão Google

## 5. Documentação Antecipada

- Antes de codar, produza:
  - Docstring para cada função/método/classe
  - Instrução breve de uso no README/SPEC.md
  - (Opcional) Fluxograma de funcionamento

## 6. Planejamento dos Testes

- Projete testes para cada funcionalidade/entrada/saída prevista (TDD opcional)
- Defina casos de uso válidos, inválidos, edge cases

## 7. Implementação Modular

- Implemente cada função/método seguindo fielmente o contrato SPEC.md
- Use type hints, validações e raises explícitos onde necessário
- Integre utilitários já existentes quando possível

## 8. Testes Unitários e Validação

- Implemente e execute os testes definidos
- Garanta cobertura para todos os casos relevantes (não perseguir cobertura cega)
- Ajuste a implementação até passar em todos os testes

## 9. Integração Inicial

- Teste o módulo isoladamente e depois integrado a uma parte do pipeline (quando aplicável)
- Simule a chamada pelos consumidores diretos
- Teste integração cross-módulos (ex: RiskManager, Logger)

## 10. Documentação Final

- Complete a documentação no README do diretório ou SPEC.md do módulo:
  - Assinaturas finais, exemplos de uso, dicas, edge cases
  - Documente dependências, integração e logs gerados

## 11. Auditoria e Evidência

- Gere evidências de execução dos testes (logs, outputs, arquivos de auditoria)
- Valide que artefatos de uso (logs, arquivos, métricas) são gerados nos locais certos

## 12. Checklist Final

- [ ] SPEC/documentação completa e versionada (`docs/specs/SPEC_NomeModulo.md`)
- [ ] Código aderente à especificação
- [ ] Testes cobrindo todos os casos relevantes e edge cases
- [ ] Evidências/auditoria salvas e versionadas
- [ ] Integração testada com módulos do pipeline
- [ ] Módulo pronto para reuso, integração e documentação pública

---

## Resumo Visual do Fluxo

1. Definir objetivo
   ↓
2. Analisar dependências/entradas/saídas
   ↓
3. Especificar formalmente (SPEC.md)
   ↓
4. Desenhar API
   ↓
5. Documentar antes de codar
   ↓
6. Planejar testes
   ↓
7. Implementar módulo
   ↓
8. Testar e validar
   ↓
9. Integrar e testar cross-módulos
   ↓
10. Documentação final (README/SPEC.md)
    ↓
11. Auditar/gerar evidências
    ↓
12. Checklist final
# 📋 CHECKLIST DE RASTREAMENTO DE MÓDULOS — Op_Trader

## Etapa 1 — Levantamento e Registro
- [ ] Verificar no `REFERENCE_TABLE.md` se o módulo já existe ou é reaproveitável
- [ ] Definir se será novo ou irá compor/herdar/utilizar módulos existentes
- [ ] Incluir linha no `DEVELOP_TABLE.md` com status inicial (@PLAN), import path, assinatura, dependências

## Etapa 2 — Criação e Registro da SPEC
- [ ] Criar arquivo `SPEC_<nome_modulo>.md` em `/docs/specs/` baseado no `SPEC_TEMPLATE.md`
- [ ] Especificar objetivo, assinatura, entradas/saídas, integração com utilitários existentes
- [ ] Documentar exemplos reais de uso e edge cases
- [ ] Referenciar módulos/utilitários reaproveitados (links cruzados)
- [ ] Atualizar DEVELOP_TABLE.md com status @SPEC e link para SPEC

## Etapa 3 — Contrato e Prototipagem
- [ ] Definir assinatura completa, métodos, argumentos, tipo de retorno (seguindo padrão FeatureCalculator)
- [ ] Adicionar docstrings padronizados para classe, init, métodos
- [ ] Explicitar dependências/imports no início do módulo

## Etapa 4 — Integração e Documentação
- [ ] Incluir exemplos de uso integrando com módulos existentes (`get_logger`, `ScalerUtils`, `save_dataframe`, etc.)
- [ ] Especificar no SPEC e docstring como importar e utilizar os utilitários reaproveitados
- [ ] Atualizar REFERENCE_TABLE.md quando o módulo for publicado (@CODED/@STABLE)
- [ ] Garantir rastreabilidade dos arquivos gerados (doc, log, SPEC, exemplos)

## Etapa 5 — Qualidade e Padronização
- [ ] Checar alinhamento com padrões do projeto (logging central, modularidade, exceptions, testes)
- [ ] Checklist de qualidade/validação no final do SPEC (tests, docs, exemplos, integração)
- [ ] Marcar como @CODED no DEVELOP_TABLE.md somente após código, doc e testes completos

## Observação
> Este checklist deve ser incluído, revisado e adaptado em todos os ciclos de desenvolvimento/reestruturação de módulos no Op_Trader.
> Permite rastrear evolução, reuso e garantir conformidade com as boas práticas do projeto.

---

**Modelo de uso:**  
- Anexe este checklist ao SPEC ou à issue de cada módulo.
- Atualize o status conforme avança cada etapa.
- Reaproveite para qualquer pipeline ou componente do Op_Trader.


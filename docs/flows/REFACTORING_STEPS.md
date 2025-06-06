# 🚦 Fluxo/Passos para Refatoração e Validação de Módulo Existente

> **Atenção**: Toda documentação gerada deve seguir o template oficial `docs/templates/SPEC_TEMPLATE.md` e estar versionada em `docs/specs/`.

## 1. Identificação do Módulo Candidato

- Escolher o módulo a ser validado/refatorado, priorizando os críticos para o pipeline (ex: execução, gestão de posição)

## 2. Preparação do Processo

- Definir abordagem **bloco a bloco** para facilitar revisão incremental
- Cada ajuste/bug deve ser destacado e explicado linha a linha durante a refatoração

## 3. Revisão do Código e Testes Existentes

- Executar e analisar os testes atuais
- Identificar falhas, dependências de caminho/import, limitações do ambiente
- Validar pontos cegos, logs ausentes, diferenças numéricas

## 4. Padronização e Ambiente de Testes

- Corrigir imports (utilizando ensure_project_root)
- Ajustar e criar testes robustos para todos edge cases
- Confirmar geração de logs no padrão auditável do projeto

## 5. Correção de Bugs e Refinamento

- Rodar os testes, ajustar asserções (ex: tolerância float)
- Garantir que logs, históricos e outputs sigam o padrão

## 6. Expansão de Cobertura e Multiativo

- Criar testes multimercado (ex: EURUSD e USDJPY simultâneos)
- Garantir que logs sejam gerados por símbolo/mercado individualmente

## 7. Aprimoramento de Flexibilidade

- Discutir precisão de casas decimais, logs, multimercado, parametrização dinâmica
- Definir adaptação automática para diferentes instrumentos

## 8. Documentação Técnica (SPEC.md)

- Gerar/atualizar documentação do módulo em `docs/specs/SPEC_NomeModulo.md` conforme template
- Interface pública, entradas/saídas, exemplos, regras, edge cases, dependências

## 9. Validação Completa

- Testar cobertura (unitários, multimercado, edge cases)
- Checar que documentação, logs e outputs seguem padrão enterprise
- Garantir evidências em local apropriado (ex: logs, arquivos, outputs)

## 10. Geração de Auditoria

- Criar arquivos de auditoria e evidências de funcionamento, logs e checklists

## 11. Planejamento para Reutilização e Integração

- Validar que o módulo está pronto para uso em pipeline de treino e execução real
- Testar integração com outros módulos-chave (ex: RiskManager, Logger, State)

## 12. Checklist Final

- [ ] Todos bugs corrigidos/documentados
- [ ] Testes cobrindo uso real, edge e integração
- [ ] SPEC/documentação e auditoria versionadas (`docs/specs/SPEC_NomeModulo.md`)
- [ ] Pronto para reuso/integrado ao pipeline
- [ ] Exemplos/documentação de uso revisados e atualizados

---

## Resumo Visual do Fluxo

1. Identificar módulo candidato
   ↓
2. Preparar processo (bloco a bloco)
   ↓
3. Revisar código/testes existentes
   ↓
4. Padronizar ambiente de testes/imports/logs
   ↓
5. Corrigir bugs/refinar
   ↓
6. Expandir cobertura/multiativo
   ↓
7. Aprimorar flexibilidade
   ↓
8. Documentar (SPEC.md)
   ↓
9. Validar cobertura/logs
   ↓
10. Gerar auditoria
    ↓
11. Planejar reutilização/integrar
    ↓
12. Checklist final
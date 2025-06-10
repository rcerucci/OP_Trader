# 📋 CHECKLIST AUTOMATIZADO — Desenvolvimento de Pipeline (Op_Trader)

## Etapa 1 — Definição Inicial e Registro
- [ ] Descrever objetivo do pipeline e escopo macro no DEV_LOG.md
- [ ] Incluir entrada no SUMMARY.md/REFERENCE_TABLE.md
- [ ] Verificar módulos, utilitários e métodos já validados para reaproveitamento (REFERENCE_TABLE.md)
- [ ] Planejar estrutura inicial de diretórios e arquivos

## Etapa 2 — Especificação Conceitual
- [ ] Criar documento de especificação conceitual (`ESPEC_CONCEITUAL_<pipeline>.md`)
- [ ] Descrever arquitetura macro, tipos de módulos, fluxos principais
- [ ] Definir contratos, requisitos, princípios de modularidade, rastreabilidade, logging e segurança

## Etapa 3 — Fluxogramas e Documentação Visual
- [ ] Gerar fluxogramas dos principais fluxos do pipeline (treinamento, execução, integração, logging)
- [ ] Salvar arquivo markdown/diagrama para consulta e reuso

## Etapa 4 — Lista e Rastreamento de Módulos
- [ ] Elaborar lista completa de módulos (essenciais e opcionais) — LISTA_MODULOS_<pipeline>.md
- [ ] Para cada módulo, verificar existência/utilização de métodos/classes do REFERENCE_TABLE.md
- [ ] Planejar possíveis wrappers, componentes plugáveis, integrações

## Etapa 5 — DEVELOP_TABLE.md e SPECs
- [ ] Criar DEVELOP_TABLE_<pipeline>.md com:
    - Caminho de importação, assinatura, dependências, descrição, status, link SPEC
- [ ] Para cada módulo novo, criar SPEC_<modulo>.md usando SPEC_TEMPLATE.md
- [ ] Referenciar explicitamente métodos/utilitários já validados e como utilizá-los no novo pipeline

## Etapa 6 — Contratos, Prototipagem e Documentação
- [ ] Especificar contratos, assinaturas, entradas/saídas e exemplos de uso real para cada módulo
- [ ] Integrar logging, rastreabilidade, normalização, salvamento, etc., sempre usando os métodos já validados do projeto
- [ ] Atualizar DEVELOP_TABLE.md e REFERENCE_TABLE.md conforme avanço do status (@PLAN, @SPEC, @CODED, @STABLE)

## Etapa 7 — Testes e Qualidade
- [ ] Definir e documentar testes unitários e de integração para todos os módulos
- [ ] Garantir reprodutibilidade dos fluxos testados (dados, logs, outputs, evidências)
- [ ] Checklist de qualidade revisado ao final de cada SPEC

## Etapa 8 — Documentação e Padronização Final
- [ ] Gerar README.md do pipeline e dos principais diretórios
- [ ] Documentar dependências e pontos de integração (com outros pipelines, brokers, ML, etc.)
- [ ] Atualizar DEV_LOG.md e SUMMARY.md com todos os arquivos/documentos gerados

## Observações finais
> Este checklist deve ser usado e adaptado para qualquer novo pipeline criado ou reestruturado no Op_Trader.  
> **Sempre reutilize métodos, utilitários e padrões já validados, evitando retrabalho e mantendo rastreabilidade.**

---

# Banco de Dados — AVIVA

Schema relacional em **MySQL** com **14 tabelas e 16 chaves estrangeiras**, abrangendo os domínios de Comunidade/Território e Saúde/Reabilitação.

## Conteúdo

- [`sql/01_schema_mysql.sql`](sql/01_schema_mysql.sql): definição do modelo.
- [`sql/02_carga_dados.sql`](sql/02_carga_dados.sql): carga SQL integral.
- [`sql/03_consultas_evidencias.sql`](sql/03_consultas_evidencias.sql): consultas de auditoria.
- [`diagramas/`](diagramas/): modelos MER/DER editáveis (.dot, .svg) e imagens (.png).
- [`testes/testar_integridade_base.py`](testes/testar_integridade_base.py): validação offline dos arquivos.

Dados analisados: 2.647 estabelecimentos, 448 posições geográficas conferidas, 478 áreas UBS, 604 registros climáticos e 4.000 eventos **simulados**. Os dados de entrada encontram-se em `modulos/comunidade/data/` e `modulos/reabilitacao/data/` para evitar duplicação de arquivos volumosos.

### Executar a auditoria offline

```bash
python banco-de-dados/testes/testar_integridade_base.py
```

### Atenção

Execute os SQLs apenas em banco MySQL 8.x de testes, com backup prévio; a carga não é idempotente. Este banco ainda não alimenta diretamente o portal, e os alertas são demonstrativos. A existência de um cadastro de saúde **não** garante serviço em funcionamento ou disponibilidade.

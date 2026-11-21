# Testes e evidências técnicas — AVIVA

## Execução offline nesta revisão (21/11/2026)

| Conjunto | Resultado | Alcance |
|---|---|---|
| Comunidade | **69 testes aprovados** | Regras e interface do módulo |
| Saúde/Reabilitação | **71 testes aprovados** | API, mapa e serviços |
| Lambda de referência reconstruída | **7 testes aprovados** | JSON, nível de água, chuva, erro e risco combinado |
| Auditoria de dados | **Aprovada** | Integridade dos CSVs e contagens documentadas |

Os testes são locais: **não** substituem testes funcionais de RDS, IAM, S3 e Lambda em conta AWS real.

## Evidência da instalação AWS — 19/11/2026

Registros da implementação anterior demonstram:
- evento ObjectCreated no S3 e processamento automático pela Lambda;
- acesso ao RDS MySQL e consulta de 2.647 estabelecimentos;
- ingestão simulada de leitura #5 com 225 cm;
- trigger SQL gerando alerta crítico #5;
- uso de VPC e camada PyMySQL no runtime Python 3.12.

Os PDFs de captura não foram incluídos nesta revisão de portfólio por conterem dados de ambiente/conta que devem ser verificados antes da divulgação.

## Limites

Os alertas são **experimentais**. O portal ainda usa as APIs/arquivos existentes e não busca esses alertas diretamente no RDS. Os notebooks de IA não estão ligados ao endpoint de produção.

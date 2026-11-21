# Inventário de código e procedência — AVIVA

**Desenvolvido por Caio Nicolav e Leonardo da Silva.** A versão pública organiza os arquivos em módulos e preserva a origem de cada implementação.

| Domínio | Arquivos públicos | Situação |
|---|---|---|
| Portal e PWA | `portal.py`, `site/` | Código original; interface, imagens e estilos preservados |
| Comunidade | `modulos/comunidade/` | Python, API, regras, clima e testes originais |
| Saúde/Reabilitação | `modulos/reabilitacao/` | API FastAPI, mapas, auditoria CNES e testes originais |
| Banco MySQL | `banco-de-dados/sql/` | Schema, carga e consultas originais |
| MER/DER | `banco-de-dados/diagramas/` | SVG, PNG e DOT originais |
| ESP32 / Wokwi | `iot/esp32-simulador/` | Firmware e circuito originais |
| IA / Machine Learning | `machine-learning/` | Notebooks originais |
| AWS S3 → Lambda → RDS | `infra/aws/` | Arquitetura comprovada por teste; Lambda é reconstrução de referência |
| Trigger de alerta | `infra/aws/sql/01_trigger_alerta_critico.sql` | SQL original recuperado |
| Restrições de duplicidade | `infra/aws/sql/02_unicidade_idempotencia.sql` | Migração de referência reconstruída |

## Registro de fidelidade

O arquivo-fonte **literal** da Lambda que executou em 19/11/2026 não estava nos anexos recuperados. Sua referência publicada foi reconstruída e tem testes próprios; não é uma cópia declarada do deploy original. O SQL do trigger foi preservado da implementação anterior.

A estrutura SQL completa foi publicada. A base exploratória CNES de 27.779 registros foi compactada em 5 partes verificadas por SHA-256 e carregada automaticamente pelo módulo, sem perda dos dados do CSV original.

A versão pública contém um novo histórico Git; o fork privado anterior foi preservado. Atribuímos a concepção e o desenvolvimento aos dois autores sem inventar divisões individuais de contribuição.

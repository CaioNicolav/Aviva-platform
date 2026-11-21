# Estado técnico real — AVIVA

AVIVA é um projeto público de software **em desenvolvimento**, concebido e desenvolvido por **Caio Nicolav e Leonardo da Silva**.

| Componente | O que existe | O que ainda não está pronto |
|---|---|---|
| Portal web | Interface responsiva e rotas integradas por `portal.py` | Autenticação real |
| Comunidade | Python, dados climáticos, interface territorial e mural local | Mural público moderado ou monitoramento de risco real |
| Saúde e reabilitação | API FastAPI, dados CNES, busca e mapa com validação geográfica | Garantir vagas e atendimento em tempo real |
| Dados MySQL | 14 tabelas, 16 FKs, views, carga e verificações | Integração do banco RDS ao portal |
| AWS / IoT | Pipeline S3 → Lambda → RDS → trigger validado com medições simuladas | Telemetria física e operação 24/7 |
| IA / ML | Notebooks experimentais | Inferência em produção conectada à aplicação |

**Proveniência:** 2.647 cadastros de saúde, 448 localizações conciliadas; 604 observações históricas de clima; 4.000 eventos comunitários simulados. Cadastros e mapas não certificam serviços disponíveis, e dados históricos não são previsão ao vivo.

O projeto deve ser avaliado pela implementação técnica existente e sua evolução documentada; funcionalidades futuras não devem ser apresentadas como já implantadas.

# Limites provisórios

Os valores abaixo reproduzem a configuração atual, não são critérios oficiais nem uma recomendação de segurança.

| Variável | Faixa aceita | Atenção a partir de | Crítico a partir de |
|---|---:|---:|---:|
| Nível da água (cm) | 0–300 | 120 | 200 |
| Intensidade da chuva (mm/h) | 0–200 | 25 | 50 |

- **Implementado:** usa o pior nível; se ambas as variáveis alcançam ao menos ATENÇÃO, o resultado combinado é CRÍTICO.
- **Testado em simulação:** fronteiras e quatro cenários no modo demo.
- **Evolução futura:** validar variáveis, unidades e limites conforme o PDF oficial de IoT/AICSS.

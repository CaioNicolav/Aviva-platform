# Fontes de dados a baixar manualmente

Os caminhos abaixo são nomes esperados para os arquivos baixados, não URLs nem
nomes oficiais dos distribuidores. Nenhuma fonte está presente em `data/raw/`
neste momento. Após o download, inspecione o cabeçalho, separador, decimal,
codificação e linhas de metadados antes de implementar/adaptar o parser.

| Fonte | O que contém | Caminho esperado em `data/raw/` | Status |
|---|---|---|---|
| INMET — chuva e clima | Observações horárias do clima (chuva, pressão, temperatura, umidade, vento) para estações A701 e A771 | `data/raw/INMET_SE_SP_A701_...CSV` e `data/raw/INMET_SE_SP_A771_...CSV` | baixado |
| ANA/CEMADEN — nível de rio | Observações de nível de rio; formato, estações e unidades dependem do arquivo escolhido | `data/raw/ana_cemaden_nivel_rio.csv` | a baixar |
| Atlas Digital de Desastres | Registros de desastres; período, campos e geografia dependem do arquivo escolhido | `data/raw/atlas_desastres.csv` | a baixar |
| IPVS | Indicador de vulnerabilidade social; escala, ano e recorte dependem do arquivo escolhido | `data/raw/ipvs.csv` | a baixar |

Não há URLs listadas porque ainda não foram verificadas. Os scripts de ingestão
informam a fonte e o caminho que precisam ser fornecidos; eles não simulam nem
preenchem dados reais ausentes.

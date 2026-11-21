# Dicionário de dados

## O que é real e o que é simulado

Os dados climáticos usados na previsão de chuva forte são reais e foram obtidos
em `data/raw/` de estações INMET do período 2026-01-01 a 2026-10-31. O formato
real exige 8 linhas de metadados, separador `;`, decimal `,`, codificação
`latin-1`, uma coluna vazia extra ao fim e horários em UTC antes da conversão
para `America/Sao_Paulo`.

O módulo de violência continua simulado: os distritos usam códigos neutros
(`D01` a `D20`), a semente é fixa e o conjunto de dados não representa ocorrências
reais de violência. Não há associação com nomes ou códigos de distritos
administrativos reais, e apenas eventos da última semana simulada podem ficar
`em_aberto`; eventos anteriores são encerrados como atendidos ou cancelados.

A tabela `data/processed/aviva_clima_diario.csv` tem uma linha por estação e dia
local, com atributos do dia D e campos defasados em relação ao passado. Ela não
contém um rótulo de classe fixo. No experimento de ML tradicional, o limiar de
"chuva forte" é o percentil 90 de `chuva_amanha_mm` calculado somente no treino;
esse mesmo limiar é aplicado ao teste para evitar vazamento de informação.

## Colunas de eventos simulados

O arquivo gerado `data/processed/eventos_violencia_simulados.csv` contém:

| Coluna | Significado | Unidade/formato | Origem | Fonte | Limitações |
|---|---|---|---|---|---|
| `id_evento` | Identificador aleatório do registro, sem ligação com pessoa | UUID v4 | simulado | Gerador local com `uuid4` | Não é identificador de uma ocorrência real; IDs variam entre execuções |
| `tipo` | Categoria sintética do registro | `alerta` ou `denuncia` | simulado | Gerador local, com semente fixa | Probabilidades são parâmetros demonstrativos, não estimativas |
| `distrito` | Grupo territorial fictício | Código neutro `D01`, `D02`, ... | simulado | Gerador local | Não pode ser relacionado a distritos administrativos reais |
| `data_hora` | Hora sintética atribuída ao registro | Data e hora ISO 8601, arredondada para hora | simulado | Gerador local | Distribuição temporal artificial; não indica padrão de violência real |
| `status` | Estado sintético do registro | `atendido`, `cancelado` ou `em_aberto` | simulado | Gerador local | Cancelamentos/falsos alertas são apenas hipótese de simulação, sem verificação |
| `origem` | Identifica a natureza dos dados | `simulado` | simulado | Constante do gerador | Deve permanecer rotulado como simulado em todo uso e apresentação |

O gerador não cria nome, telefone, endereço, coordenada exata ou outro campo
pessoal. UUIDs não tornam os eventos observações reais nem permitem identificar
uma pessoa.

O arquivo regenerado contém 4.000 eventos no período de 2026-01-01 a
2026-10-31, distribuídos pelos 20 códigos neutros. Isso corresponde a uma média
de 4,55 eventos por distrito por semana (44 semanas de calendário); os pesos
fixos diferentes por distrito produzem volumes distintos. Foram observados de
115 a 382 eventos por distrito. Na geração atual, 6 eventos da última semana
ficaram `em_aberto` e nenhum evento anterior a 2026-10-25 ficou nesse estado.

## Colunas dos arquivos semanais normalizados

Os arquivos abaixo são contratos de saída para futuros parsers. Só devem ser
produzidos após baixar e inspecionar os arquivos originais. Datas/medidas não
serão inferidas quando a fonte estiver ausente.

O montador espera os seguintes CSVs normalizados em `data/processed/`:
`chuva_semanal.csv` (`distrito`, `semana`, `chuva_mm`),
`nivel_rio_semanal.csv` (`distrito`, `semana`, `nivel_rio_m`),
`desastres_semanal.csv` (`distrito`, `semana`, `total_desastres`) e
`ipvs_semanal.csv` (`distrito`, `semana`, `ipvs`). Esses arquivos ainda não
existem; seus parsers dependem da inspeção dos originais.

| Coluna | Significado | Unidade/formato | Origem | Fonte | Limitações |
|---|---|---|---|---|---|
| `distrito` | Distrito administrativo conforme a fonte original | Texto conforme fonte | real | Fonte oficial da respectiva tabela em `fontes.md` | O mapeamento entre estação/local de medição e distrito precisa ser documentado; não presumir correspondências |
| `semana` | Semana ISO associada ao registro | `AAAA-Www` | real | Data da fonte original | Granularidade semanal pode ocultar variações dentro da semana |
| `chuva_mm` | Precipitação agregada na semana | mm/semana | real | INMET | Regra de agregação, cobertura e estação de referência devem ser documentadas pelo parser |
| `nivel_rio_m` | Nível de rio agregado para a semana | m | real | ANA/CEMADEN | Definição da medição e regra semanal dependem do arquivo baixado |
| `total_desastres` | Quantidade de registros de desastre na semana | ocorrências/semana | real | Atlas Digital de Desastres | Registro histórico não é previsão; deduplicação e geografia dependem da fonte |
| `ipvs` | Valor do indicador de vulnerabilidade social da fonte | Escala/unidade conforme publicação | real | IPVS | A escala, ano de referência e unidade geográfica devem ser preservados conforme o arquivo original |
| `total_alertas` | Alertas sintéticos agregados na semana | eventos/semana | simulado | Agregação de `eventos_violencia_simulados.csv` | Não representa alertas enviados por usuárias reais |
| `total_denuncias` | Denúncias sintéticas agregadas na semana | eventos/semana | simulado | Agregação de `eventos_violencia_simulados.csv` | Não representa denúncias reais |
| `alertas_atendidos` | Alertas sintéticos com status atendido | eventos/semana | simulado | Agregação de `eventos_violencia_simulados.csv` | Não há atendimento real |
| `alertas_cancelados` | Alertas sintéticos com status cancelado | eventos/semana | simulado | Agregação de `eventos_violencia_simulados.csv` | Não é uma classificação verificada de falso alerta |
| `alertas_em_aberto` | Alertas sintéticos ainda em aberto | eventos/semana | simulado | Agregação de `eventos_violencia_simulados.csv` | Estado gerado artificialmente |
| `denuncias_atendidas` | Denúncias sintéticas com status atendido | eventos/semana | simulado | Agregação de `eventos_violencia_simulados.csv` | Não há atendimento real |
| `denuncias_canceladas` | Denúncias sintéticas com status cancelado | eventos/semana | simulado | Agregação de `eventos_violencia_simulados.csv` | Estado gerado artificialmente |
| `denuncias_em_aberto` | Denúncias sintéticas ainda em aberto | eventos/semana | simulado | Agregação de `eventos_violencia_simulados.csv` | Estado gerado artificialmente |
| `origem_ambiental` | Rótulo de proveniência do módulo de risco ambiental | `real` | real | INMET, ANA/CEMADEN e/ou Atlas Digital de Desastres, após ingestão verificada | A coluna só existe quando ao menos uma fonte ambiental normalizada está disponível |
| `origem_vulnerabilidade` | Rótulo de proveniência do módulo de vulnerabilidade social | `real` | real | IPVS, após ingestão verificada | A coluna só existe quando a fonte normalizada está disponível |
| `origem_violencia` | Rótulo de proveniência dos eventos agregados | `simulado` | simulado | Gerador local | Deve ser mantida; códigos territoriais sintéticos não se juntam a nomes reais |

O arquivo consolidado também contém `distrito` e `semana` como chaves. A
montagem omite as colunas de uma fonte que não tenha arquivo normalizado e
emite um aviso. Não substitui ausência por números aleatórios.

## Distritos oficiais de São Paulo usados no site

`data/distritos_sao_paulo.json` contém a lista de nomes e códigos IBGE dos 96
distritos do município de São Paulo (código 3550308), obtida da
[API de localidades do IBGE](https://servicodados.ibge.gov.br/api/v1/localidades/municipios/3550308/distritos).
O arquivo preserva a data da consulta e serve como catálogo geográfico para
seleção e filtro do protótipo. Não contém população, ocorrências, limites
geográficos nem dados de moradores.

Os limites e pontos de referência exibidos no guia do território são consultados
no OpenStreetMap via Nominatim e Overpass API. A aplicação cruza cada ponto com
a geometria do distrito para evitar incluir locais fora da região. A fonte é
colaborativa e não representa um cadastro oficial da Prefeitura; sua cobertura
varia, e muitas vezes não informa se cada unidade é pública, está aberta ou
oferece determinado atendimento. O nome de distrito enviado à fonte vem do
catálogo oficial do IBGE. O bairro opcional não é enviado ao geocodificador.
Dados geográficos sob Open Database License (ODbL); consulte
[os créditos do OpenStreetMap](https://www.openstreetmap.org/copyright).

## Dataset climático diário real

Resumo do arquivo gerado em `data/processed/aviva_clima_diario.csv`:

- linhas: 604 (302 por estação)
- período: 2026-01-01 a 2026-10-29
- estações: A701 e A771
- proporção de células ausentes no CSV final: 0,144% (20 de 13.892 células)
- dias locais parciais descartados: 4 (2 por estação, medidos pelo parser)
- linhas sem `chuva_amanha_mm` descartadas: 2 (último dia elegível de cada estação)
- linhas finais com `horas_faltantes` maior que zero: 37

`horas_faltantes` conta horas em que pelo menos uma das variáveis usadas pelo
dataset está ausente: precipitação, pressão, temperatura do ar, umidade
relativa, vento médio ou rajada máxima. Radiação e outras colunas que não são
usadas no modelo não entram nessa contagem.

Distribuição medida de `horas_faltantes` no CSV final:

| Horas faltantes | Dias |
|---:|---:|
| 0 | 567 |
| 1 | 15 |
| 2 | 15 |
| 3 | 3 |
| 5 | 1 |
| 6 | 1 |
| 11 | 1 |
| 14 | 1 |

O `describe()` medido no dataset final resulta em: count=604, mean=0,149007,
std=0,879648, min=0, Q1=0, mediana=0, Q3=0, max=14. Os dois dias locais
parciais da borda (início e fim da série após conversão UTC → São Paulo) são
removidos por estação; a quantidade é calculada a partir dos registros horários
em vez de ser fixada no código.

O arquivo foi gerado a partir das estações INMET real e contém uma linha por
`estacao` e `data` local. A tabela inclui:

- atributos do dia: `chuva_dia_mm`, `chuva_max_hora_mm`, `horas_com_chuva`,
  `pressao_media_hpa`, `pressao_amplitude_hpa`, `temperatura_media_c`,
  `temperatura_max_c`, `temperatura_min_c`, `umidade_media_pct`,
  `umidade_min_pct`, `vento_medio_ms`, `rajada_maxima_ms`,
  `horas_faltantes`;
- defasagens históricas: `chuva_dia_mm_d1`, `chuva_dia_mm_d2`,
  `umidade_media_pct_d1`, `umidade_media_pct_d2`,
  `pressao_media_hpa_d1`, `pressao_media_hpa_d2`,
  `pressao_media_variacao_d1_d`;
- alvo futuro: `chuva_amanha_mm`, que representa a precipitação contínua do dia
  seguinte em mm e não deve ser usado como rótulo fixo em treinamento.

As observações com variáveis usadas ausentes são documentadas via
`horas_faltantes`; valores meteorológicos ausentes não são preenchidos com zero
em silêncio. Depois da criação do alvo contínuo, linhas sem leitura de chuva do
dia seguinte são removidas.

## Alvo de aprendizado de máquina

O notebook `notebooks/ml-tradicional.ipynb` cria um rótulo binário experimental
de chuva forte a partir do percentil 90 de `chuva_amanha_mm` no treino. O CSV
continua sem rótulo fixo. O notebook remove, apenas para modelagem, as duas
primeiras linhas de cada estação por não terem histórico completo das
defasagens; também exclui dias com `horas_faltantes > 6`, pois menos de 18 horas
observadas tornam os agregados diários pouco confiáveis.

A divisão é cronológica em 21/06/2026: treino no verão/outono e teste no
inverno/primavera do hemisfério sul. O conjunto contém 598 observações de duas
estações e menos de um ano, portanto as métricas são exploratórias e não
demonstram generalização para outros períodos ou locais. Avaliações futuras
devem ampliar o período e a cobertura e validar estabilidade temporal. O
experimento não classifica prioridade como `NORMAL`, `ATENÇÃO` ou `CRÍTICO` e
não deve ser interpretado como sistema operacional de alerta.

## Privacidade no ranking

Um ranking por distrito deve exibir resultados apenas quando houver pelo menos
`MINIMO_EVENTOS_RANKING` eventos no grupo (configuração atual: 5). Abaixo desse
limite, exibir somente **“dados insuficientes”**. O limite reduz exposição, mas
não garante anonimização; não publique registros individuais.

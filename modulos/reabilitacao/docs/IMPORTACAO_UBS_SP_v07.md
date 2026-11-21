# AVIVA v0.7 — Importação de UBS da capital paulista

## Base de origem

Arquivo **cnes_estabelecimentos_json.zip** fornecido pelo usuário, contendo **642.608** estabelecimentos no JSON de origem. A leitura foi integral, sem inventar estabelecimentos. Dados cadastrais, sem data de referência confirmada no arquivo.

## Regras conservadoras

- Município IBGE `355030` (São Paulo — capital).
- Tipo de estabelecimento `TP_UNIDADE = 2`, usado no CNES para Centro de Saúde/Unidade Básica.
- Indicador `CO_AMBULATORIAL_SUS = SIM`.
- Nome fantasia com `UBS`, `UBSI`, `UNIDADE BASICA DE SAUDE` ou `CENTRO DE SAUDE`, com normalização de acentos.

Os critérios resultaram em **487** registros cadastrados; **483** possuem os dois campos de coordenadas preenchidos, mas isso não equivale à validação geográfica. O mapa aplica limites geográficos aproximados e pode excluir coordenadas inconsistentes.

Foram mantidos separadamente os registros anteriores de CAPS, CER e outros (identificados por termos no nome) e duas oficinas documentadas institucionalmente. O registro CNES não é duplicado se já existir na camada anterior.

## Arquivos gerados

- `data/ubs_cnes_sp.csv`: registros usados na interface e API.
- `data/ubs_importacao_resumo.json`: critérios e hash do ZIP de origem.
- `app/cnes_exploratorio.py`: agrega a camada de UBS e disponibiliza filtros.
- `app/geografia.py`: mapa com as coordenadas cadastrais e pontos de proximidade.

## Avisos necessários para o cidadão

A categoria UBS representa **uma classificação cadastral confiável segundo código e nome**, mas não confirma que haja fisioterapia, terapia ocupacional, atendimento de reabilitação, disponibilidade, horários ou vagas. A UBS de referência de uma pessoa pode ser definida pelo endereço de moradia, não somente pela distância.

A indicação ambulatorial SUS (`SIM`) é reproduzida do campo do arquivo. A base precisa ser complementada por dados municipais ou validação institucional antes de oferecer garantia de serviço específico.

**Próximas etapas:** verificar o cadastro municipal e atualizar periodicamente, conferir endereços, coordenadas, contato e dados de serviço. Incluir campo de origem e data de revisão em toda futura validação.

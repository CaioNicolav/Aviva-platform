# AVIVA 0.11 — Mapa único validado geograficamente

## O que foi alterado

1. O seletor de coordenadas exploratórias foi removido da interface.
2. A API `/api/v1/reabilitacao/cnes/mapa-sp` agora recusa `modo=exploratorio` com HTTP 422.
3. Todos os pins e cálculos de proximidade derivam exclusivamente de registros com `status_auditoria=ponto_correspondente_referencia_externa`.
4. O modo **Lista + mapa** permanece como visualização padrão, com todas as categorias no catálogo e os pins geograficamente conferidos; a categoria específica continua sendo filtro opcional.
5. Os itens ainda não confirmados por base cartográfica independente continuam na lista, mas são omitidos dos pins e do cálculo dos mais próximos.
6. Mensagens antigas que diziam que a base municipal não havia sido importada foram removidas.

## Fontes já disponíveis

- `fontes_oficiais/Estabelecimentos_de_Saude_Referencia_das_AAUBS2026.kmz`
- `fontes_oficiais/Areas_de_Abrangencia_de_UBS_no_MSP_2026.kmz`
- `data/referencia_municipal_ubs_2026.csv`
- `data/cruzamento_enderecos_ubs_2026.csv`
- `data/auditoria_integral_sp.csv`

Resultado: 448 UBS com coordenadas cruzadas com a Prefeitura e endereço CNES consistente; 39 UBS do catálogo ainda não liberadas no mapa.

## O que NÃO foi comprovado

A geolocalização de CAPS, CER e oficinas ortopédicas **não foi validada** pelos KMZ de referência de UBS. Para essas categorias, é necessário obter fonte oficial geográfica específica (por exemplo, "Estabelecimentos e Serviços de Saúde SUS e Conveniados no Município de São Paulo", publicada pela Secretaria Municipal da Saúde em julho de 2024), conciliar os identificadores e os endereços e considerar a defasagem temporal. Esse arquivo não integra a versão 0.11.

A validação de posição também não comprova que o estabelecimento está atendendo, possui vagas, tem habilitação atual ou que o cidadão pode comparecer sem encaminhamento. A UBS de referência deve ser confirmada pela rede municipal.

## Como testar

```powershell
py -m uvicorn app.main:app --reload
```

Abra `http://127.0.0.1:8000/`. Por padrão, a busca mostra todas as categorias na lista e apenas as 448 UBS geograficamente conciliadas no mapa. Ao filtrar CAPS, CER ou oficinas, a lista permanece, mas o mapa não mostrará pins até existir validação cartográfica independente. O comando `py -m pytest -q` verifica os testes.

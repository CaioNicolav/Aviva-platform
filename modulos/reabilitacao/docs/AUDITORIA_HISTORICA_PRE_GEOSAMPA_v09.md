# AVIVA — Auditoria integral dos registros geográficos de São Paulo

**Data:** 2026-11-16  
**Escopo analisado:** 2,647 estabelecimentos CNES únicos no recorte de São Paulo, incluindo **635** com indicação ambulatorial SUS = SIM (filtro padrão do mapa).

## Resultado da varredura automatizada

| Situação da localização | Todos os cadastros | Registros do filtro ambulatorial SUS |
|---|---:|---:|
| ponto_correspondente_referencia_externa | 0 | 0 |
| suspeita_automatica_sem_referencia_externa | 171 | 10 |
| sem_coordenadas_confiaveis | 179 | 12 |
| pendente_validacao_em_fonte_externa | 2297 | 613 |


A revisão automatizada percorreu **100% dos 2647 registros** do recorte carregado na versão. Isso **NÃO** é validação cartográfica individual: ela exigiria localizar cada estabelecimento em fonte geográfica independente, conferir endereço/CEP/numeração e, para uso assistencial, confirmar funcionamento e condições atuais de atendimento. O arquivo externo não foi importado nesta execução: **NÃO**.

## O que foi verificado para cada registro
- Código CNES único, nome, categoria, endereço e bairro informados no cadastro, CEP e presença de número.
- Coordenadas sintaticamente válidas e dentro de uma área ampla do município.
- Distância ao agrupamento dos registros do mesmo bairro e prefixo CEP-5, apenas quando há amostras suficientes e coesas.
- Duplicidade de coordenadas arredondadas entre estabelecimentos de CEPs diferentes.
- Correspondência contra base cartográfica externa **somente quando um arquivo de referência for fornecido**; preferir correspondência exata de CNES ou correspondência única de nome+logradouro+número.

## Limitações e política do AVIVA
- Bairros e CEPs repetidos, deslocados ou inconsistentes podem não ser detectados por verificações estatísticas.
- Coordenadas coerentes com pontos próximos do CNES **não comprovam posição correta**; dados com o mesmo erro podem formar um agrupamento coerente.
- Coordenadas substituídas por referências secundárias, como a UBS Boracea na versão 0.8, **não são consideradas confirmação oficial**.
- Pontos sem referência geográfica independente **não devem ser usados em roteamento nem na função ‘mais próximos’ como opções confiáveis**.
- O CNES não assegura disponibilidade de atendimento, habilitação em reabilitação, horários ou vagas.

## Fonte oficial para próxima etapa
Metadados da camada municipal UBS/Posto/Centro de Saúde: https://metadados.geosampa.prefeitura.sp.gov.br/geonetwork/srv/api/records/bc44ee6c-e973-4670-b912-9ac8d64b9f56

Página da Prefeitura com **Estabelecimentos de Referência das Áreas de Abrangência 2026**: https://prefeitura.sp.gov.br/web/saude/w/epidemiologia_e_informacao/geoprocessamento_e_informacoes_socioambientais/265388

## Como efetuar cruzamento externo e repetir auditoria
1. Baixe a camada oficial em **KMZ/KML ou CSV/GeoJSON com lat/lon em WGS84**; não utilize imagem do mapa nem uma lista sem coordenadas.
2. Coloque o arquivo na pasta `data/`.
3. Execute: `py -m scripts.auditoria_integral --referencia "data/NOME_ARQUIVO.kmz" --fonte-url "URL_DA_FONTE"`.
4. Leia `data/resumo_auditoria_integral_sp.json` e `data/auditoria_integral_sp.csv`.
5. Reabra o servidor. Só os **pontos correspondentes à fonte independente** serão elegíveis à funcionalidade de proximidade na versão 0.9.

**Não é correto afirmar que todos os endereços foram validados.** Os casos pendentes permanecem disponíveis na pesquisa textual, com avisos para conferir a fonte oficial.

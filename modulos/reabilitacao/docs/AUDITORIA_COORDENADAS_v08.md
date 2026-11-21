# AVIVA 0.8 — Auditoria de coordenadas (São Paulo, 16/11/2026)

## Problema encontrado no teste de usuário
- UBS Boracea, CNES **6048633**: registro CNES incluía **(-23.5484296, -46.3947173)**, incompatível com seu endereço **Rua Boracea, 270, Barra Funda**.
- A Prefeitura de São Paulo confirma o endereço e o CNES: https://prefeitura.sp.gov.br/web/saude/w/coordenadorias-regionais-de-sa%C3%BAde-norte
- Uma referência cartográfica secundária apresenta **(-23.5255082, -46.6515979)**: https://www.benditoguia.com.br/empresa/basic-health-unit-ubs-boraceia-barra-funda-sao-paulo-sp
- Estas coordenadas representam uma **revisão aproximada**, ainda exigindo checagem contra a camada oficial de equipamentos GeoSampa para precisão completa.
- **CAPS AD III Boracea** é outra unidade (CNES 2960303) na Rua Anhanguera; não confundir com a UBS Boracea.

## Proteção aplicada
1. Os dados de origem CNES permanecem intocados em `data/ubs_cnes_sp.csv`.
2. `data/correcoes_geo_sp.csv` contém revisões pontuais, com fonte do endereço e da posição; o sistema usa a revisão em vez da coordenada bruta na saída do mapa.
3. `app/auditoria_geo.py` compara coordenadas com a mediana dos registros do mesmo bairro quando existem no mínimo 5 referências. Coordenadas a mais de 6 km do agrupamento são **retiradas dos pins e da busca de proximidade** até revisão.
4. O processo automático é apenas uma **triagem de anomalias**. Os pontos restantes NÃO estão individualmente validados por geocodificação e podem ter outros erros.
5. Os registros sem pin continuam nas listas de endereço; não significa ausência do serviço.

## Antes de publicar como serviço de localização confiável
- Baixar a camada georreferenciada oficial UBS/Posto/Centro de Saúde no GeoSampa: https://metadados.geosampa.prefeitura.sp.gov.br/geonetwork/srv/api/records/bc44ee6c-e973-4670-b912-9ac8d64b9f56
- Cruzar os registros por **CNES** quando disponível, ou por nome+endereço auditado. Conferir resultados ambíguos manualmente.
- Para CAPS, CER e oficinas, empregar as camadas correspondentes e cadastros institucionais específicos.
- Só então habilitar navegação de precisão e informar atendimento disponível após verificar rede SUS/habilitação.

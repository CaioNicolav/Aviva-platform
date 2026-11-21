# AVIVA 0.10 — Cruzamento geográfico das UBS com os KMZ municipais de 2026

**Data da auditoria:** 2026-11-16. Fonte: Prefeitura de São Paulo, camadas publicadas em maio de 2026, relativas à rede municipal e áreas de abrangência. A base do CNES utilizada pelo AVIVA pode ter data de atualização diferente.

## Arquivos recebidos
- `Estabelecimentos_de_Saude_Referencia_das_AAUBS2026.kmz`: 485 pontos geográficos, todos com códigos CNES únicos, endereços e coordenadas oficiais.
- `Areas_de_Abrangencia_de_UBS_no_MSP_2026.kmz`: 485 áreas atribuídas a UBS; o conjunto de CNES corresponde exatamente ao conjunto de pontos do primeiro arquivo. Esses polígonos representam **território de abrangência**, não prova de que a unidade atende hoje ou da sua entrada física.
- Hash SHA-256 primeiro KMZ: `98fd46336ce417c8fa77e4cc0571ce3065c2bf1e16456adc9872d6b48d9dc942`.
- Hash SHA-256 segundo KMZ: `3884c6032114b9734edd4ac81a71ad95fa23dc52376d8283e7c71f125331113e`.

## Resultado do cruzamento UBS (código CNES e endereço)
| Situação | Quantidade |
|---|---:|
| UBS com correspondência de CNES e compatibilidade de rua, número e CEP | **448** |
| UBS com CNES igual, mas endereço divergente ou incompleto | **29** |
| Ponto municipal fora da área da própria UBS (>100 m), revisão adicional | **1** |
| UBS do CNES AVIVA sem correspondência na camada municipal | **9** |
| Referências municipais que não estão no recorte cadastral UBS do AVIVA | **7** |

O segundo KMZ permitiu checar se o próprio ponto municipal cai na área associada ao seu CNES: **479 dentro e 6 fora**. A divergência territorial não prova erro do ponto, mas discrepâncias grandes impedem validação automática. **Um registro com endereço compatível foi bloqueado adicionalmente** por ficar cerca de 222 m fora da própria área, enquanto as outras cinco exceções já tinham conflito cadastral.

O *match* foi feito primeiro por **CNES exato e único**. Para liberar o pin também exigimos **CEP, número e logradouro compatíveis**. Nomes e códigos iguais isoladamente não são suficientes. As posições para os 448 casos liberados passaram a usar as **coordenadas da camada oficial municipal** — sem editar o endereço bruto do CNES. O relatório contém os dois endereços para revisão, e os casos de conflito não podem ser usados em “mais próximos”.

Das UBS com endereço consistente, 38 apresentavam discrepância de **1 km ou mais** entre o ponto antigo do CNES e o ponto municipal, ilustrando o problema que afetava o AVIVA.

### Exemplo — UBS Boracea (CNES 6048633)
- Endereço municipal: `R. BORACEA 270`; cadastro CNES: `RUA BORACEA 270`.
- Diferença entre coordenadas do CNES e da Prefeitura: **26.3 km**.
- Status: `endereco_consistente_2_fontes`. O pin liberado usa o **ponto oficial do município**, não a coordenada antiga do CNES.

## Escopo de segurança e pendências
- **Somente UBS** puderam ser cruzadas com os KMZ enviados. A localização de **CAPS, CER, oficinas ortopédicas e outros** não foi validada por esses KMZ e permanece pendente de fontes cartográficas específicas.
- Há **29** UBS com endereço divergente: são pesquisáveis no catálogo, mas sem ponto seguro até revisão manual dos dados.
- Os **9** cadastros adicionais da versão CNES podem ser estabelecimentos abertos após a data do mapa municipal ou não constar por outro motivo — não concluir fechamento a partir da ausência no KMZ.
- Os **7** registros exclusivos do município não foram adicionados automaticamente como UBS à base do AVIVA, pois podem representar categorias distintas. Exigem revisão.
- **Ponto geográfico oficial não significa entrada exata, disponibilidade, vaga, habilitação de reabilitação ou atendimento sem encaminhamento.** Ainda requer confirmação do serviço.
- O segundo KMZ pode apoiar uma futura função **“encontrar UBS de referência”** por interseção geográfica da posição fornecida voluntariamente pelo cidadão; a região administrativa não é sinônimo de bairro nem de proximidade, e a referência territorial deve ser confirmada na rede de saúde.

## Arquivos produzidos
- `data/referencia_municipal_ubs_2026.csv`: 485 pontos municipais com identificação CNES, localização e endereço.
- `data/checagem_ponto_dentro_area_2026.csv`: relação de 485 UBS, informando se o ponto municipal está dentro de sua área de abrangência.
- `data/areas_abrangencia_ubs_2026_resumo.csv`: resumo CNES de 485 polígonos (geometria íntegra preservada no KMZ original).
- `data/cruzamento_enderecos_ubs_2026.csv`: 494 linhas de conciliação UBS do AVIVA x dados da Prefeitura, com motivos de revisão.
- `data/auditoria_integral_sp.csv`: resultados dos 2647 cadastros do AVIVA, com posição oficial somente para correspondências de UBS seguras.
- `data/resumo_auditoria_integral_sp.json`: totais e escopo atualizado.
- `fontes_oficiais/`: ambos os KMZ originais recebidos, para auditabilidade.

Fonte municipal: https://prefeitura.sp.gov.br/web/saude/w/epidemiologia_e_informacao/geoprocessamento_e_informacoes_socioambientais/265388

**Conclusão:** houve conferência cruzada automática de todos os registros disponíveis no AVIVA, mas não confirmação individual de todos os locais nem de sua situação operacional. A validação geográfica segura do mapa da versão 0.10 alcança 448 UBS do recorte atual.

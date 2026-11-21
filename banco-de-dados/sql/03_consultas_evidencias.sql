-- AVIVA | Consultas para analisar volumes, categorias e consistência dos registros.
-- Alguns eventos, leituras e classificações presentes no banco são simulados.
USE aviva_gs_2026;
SELECT 'saude_estabelecimentos' AS tabela, COUNT(*) AS total FROM estabelecimento_saude
UNION ALL SELECT 'geografia_auditada',COUNT(*) FROM validacao_localizacao
UNION ALL SELECT 'ubs_abrangencia',COUNT(*) FROM area_abrangencia_ubs
UNION ALL SELECT 'clima_diario',COUNT(*) FROM clima_diario
UNION ALL SELECT 'eventos_comunitarios_simulados',COUNT(*) FROM evento_comunitario
UNION ALL SELECT 'leituras_iot_exemplo',COUNT(*) FROM leitura_iot;
SELECT id_categoria,COUNT(*) AS total FROM estabelecimento_saude GROUP BY id_categoria ORDER BY total DESC;
SELECT e.id_categoria,v.posicao_verificada,COUNT(*) AS total FROM estabelecimento_saude e
JOIN validacao_localizacao v ON v.cnes=e.cnes GROUP BY e.id_categoria,v.posicao_verificada;
SELECT cnes,nome,id_categoria,bairro_cnes,selo_mapa,aviso FROM vw_servicos_mapa
WHERE id_categoria IN ('UBS','CAPS','CER','OFICINA') LIMIT 30;
SELECT e.cnes,e.nome,e.latitude_cnes,e.longitude_cnes,v.latitude_pin_verificado,v.longitude_pin_verificado
FROM estabelecimento_saude e JOIN validacao_localizacao v ON v.cnes=e.cnes WHERE e.cnes='6048633';
SELECT codigo_estacao,COUNT(*) AS dias,ROUND(AVG(chuva_dia_mm),2) AS chuva_media_mm,
ROUND(MAX(chuva_dia_mm),2) AS chuva_max_mm FROM clima_diario GROUP BY codigo_estacao;
SELECT origem,tipo,COUNT(*) AS total FROM evento_comunitario GROUP BY origem,tipo;
SELECT id_leitura,data_hora,nivel_agua_cm,chuva_simulada_mm_h,situacao,natureza,orientacao
FROM vw_leituras_alertas ORDER BY data_hora;
SELECT COUNT(*) AS sem_estabelecimento FROM validacao_localizacao v
LEFT JOIN estabelecimento_saude e ON e.cnes=v.cnes WHERE e.cnes IS NULL;
SELECT COUNT(*) AS modalidades_comprovadas FROM estabelecimento_modalidade;

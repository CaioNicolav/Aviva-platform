-- AVIVA GS | Consultas de evidencias para o MySQL Workbench
USE aviva_gs_2026;
-- 1. Contagem por modulo e tipo de dado
SELECT 'saude_estabelecimentos' AS tabela, COUNT(*) AS total FROM estabelecimento_saude
UNION ALL SELECT 'geografia_auditada',COUNT(*) FROM validacao_localizacao
UNION ALL SELECT 'ubs_abrangencia',COUNT(*) FROM area_abrangencia_ubs
UNION ALL SELECT 'clima_diario',COUNT(*) FROM clima_diario
UNION ALL SELECT 'eventos_comunitarios_simulados',COUNT(*) FROM evento_comunitario
UNION ALL SELECT 'leituras_iot_exemplo',COUNT(*) FROM leitura_iot;
-- 2. Categorias, com ressalva: OUTROS nao prova reabilitacao
SELECT id_categoria,COUNT(*) AS total FROM estabelecimento_saude GROUP BY id_categoria ORDER BY total DESC;
-- 3. UBS conferidas x pendentes
SELECT e.id_categoria,v.posicao_verificada,COUNT(*) AS total FROM estabelecimento_saude e
JOIN validacao_localizacao v ON v.cnes=e.cnes GROUP BY e.id_categoria,v.posicao_verificada;
-- 4. Unidades por bairro + status geografico
SELECT cnes,nome,id_categoria,bairro_cnes,selo_mapa,aviso FROM vw_servicos_mapa
WHERE id_categoria IN ('UBS','CAPS','CER','OFICINA') LIMIT 30;
-- 5. CNES da UBS Boracea (o ponto auditado em vez da coordenada CNES)
SELECT e.cnes,e.nome,e.latitude_cnes,e.longitude_cnes,v.latitude_pin_verificado,v.longitude_pin_verificado
FROM estabelecimento_saude e JOIN validacao_localizacao v ON v.cnes=e.cnes WHERE e.cnes='6048633';
-- 6. Série histórica de chuva, NÃO previsão de enchente
SELECT codigo_estacao,COUNT(*) AS dias,ROUND(AVG(chuva_dia_mm),2) AS chuva_media_mm,
ROUND(MAX(chuva_dia_mm),2) AS chuva_max_mm FROM clima_diario GROUP BY codigo_estacao;
-- 7. Eventos são sintéticos, não são denuncias reais
SELECT origem,tipo,COUNT(*) AS total FROM evento_comunitario GROUP BY origem,tipo;
-- 8. Leituras demonstrativas e relação 1:N, 1:1 com alerta
SELECT id_leitura,data_hora,nivel_agua_cm,chuva_simulada_mm_h,situacao,natureza,orientacao
FROM vw_leituras_alertas ORDER BY data_hora;
-- 9. Integridade referencial (esperado = 0 registros orfaos)
SELECT COUNT(*) AS sem_estabelecimento FROM validacao_localizacao v
LEFT JOIN estabelecimento_saude e ON e.cnes=v.cnes WHERE e.cnes IS NULL;
-- 10. Associações clinicas: intencionalmente zeradas, não comprovadas por nome
SELECT COUNT(*) AS modalidades_comprovadas FROM estabelecimento_modalidade;

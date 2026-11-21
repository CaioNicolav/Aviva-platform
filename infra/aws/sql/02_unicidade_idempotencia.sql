-- Migração de referência RECONSTRUÍDA a partir da regra documentada.
-- Revisar dados e fazer backup antes de executar em MySQL de testes.
USE aviva_gs_2026;
SELECT id_dispositivo, data_hora, COUNT(*) AS ocorrencias
FROM leitura_iot
GROUP BY id_dispositivo, data_hora
HAVING COUNT(*) > 1;
-- Execute somente se a consulta acima NÃO retornar duplicatas:
ALTER TABLE leitura_iot
ADD UNIQUE KEY uq_leitura_dispositivo_hora (id_dispositivo, data_hora);

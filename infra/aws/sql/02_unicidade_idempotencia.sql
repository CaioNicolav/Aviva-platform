-- AVIVA | Restringe leituras duplicadas por dispositivo e horário.
-- Verifique duplicidades e faça backup antes de executar a migração.
USE aviva_gs_2026;
SELECT id_dispositivo, data_hora, COUNT(*) AS ocorrencias
FROM leitura_iot
GROUP BY id_dispositivo, data_hora
HAVING COUNT(*) > 1;
ALTER TABLE leitura_iot
ADD UNIQUE KEY uq_leitura_dispositivo_hora (id_dispositivo, data_hora);

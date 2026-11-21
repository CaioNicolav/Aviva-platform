-- Garante idempotência pela combinação entre dispositivo e horário da leitura.
-- Verifique duplicidades na consulta abaixo e faça backup antes de aplicar a chave única.
USE aviva_gs_2026;
SELECT id_dispositivo, data_hora, COUNT(*) AS ocorrencias
FROM leitura_iot
GROUP BY id_dispositivo, data_hora
HAVING COUNT(*) > 1;
-- A criação da restrição exige ausência de registros repetidos na combinação.
ALTER TABLE leitura_iot
ADD UNIQUE KEY uq_leitura_dispositivo_hora (id_dispositivo, data_hora);

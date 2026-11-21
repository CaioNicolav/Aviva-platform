-- AVIVA | Cria a trigger de alerta experimental ao registrar nível de água crítico.
-- Este script recria a trigger no MySQL e não gera avisos oficiais à população.
USE aviva_gs_2026;

DROP TRIGGER IF EXISTS trg_alerta_critico;

CREATE TRIGGER trg_alerta_critico
AFTER INSERT ON leitura_iot
FOR EACH ROW
INSERT INTO alerta_iot (id_leitura, nivel, orientacao, gerado_em)
SELECT NEW.id_leitura,
       'CRITICO',
       'Nível de água elevado. Alerta experimental; não utilizar como alerta público.',
       NOW()
WHERE NEW.nivel_agua_cm >= 200.000;

SHOW TRIGGERS FROM aviva_gs_2026 LIKE 'leitura_iot';
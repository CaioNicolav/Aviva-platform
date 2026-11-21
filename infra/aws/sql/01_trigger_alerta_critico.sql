-- Trigger de alerta crítico associada à inserção de uma leitura IoT.
-- O campo gerado_em registra a criação do alerta; o script recria a trigger.
-- Limiar experimental de 200 cm: não representa alerta oficial de Defesa Civil.
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
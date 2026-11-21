"""Processa arquivos JSON recebidos do S3 e grava medições no RDS MySQL.

Fluxo: identifica novos objetos no prefixo configurado, valida os campos,
classifica o nível de atenção e persiste a leitura de forma idempotente.
Implementação de referência sujeita à configuração e validação do ambiente AWS.
As medições de exemplo não constituem alertas oficiais à população.
"""
import json
import logging
import math
import os
from datetime import datetime, timezone
from decimal import Decimal
from urllib.parse import unquote_plus

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)

# Valida os campos de entrada e aplica os limiares de risco configurados.
def parse_measurement(payload):
    if not isinstance(payload, dict):
        raise ValueError("JSON precisa conter um objeto")
    raw_time = payload.get("data_hora") or payload.get("timestamp")
    if not raw_time:
        raise ValueError("data_hora obrigatória")
    if isinstance(raw_time, (int, float)):
        dt = datetime.fromtimestamp(raw_time, tz=timezone.utc).replace(tzinfo=None)
    else:
        dt = datetime.fromisoformat(str(raw_time).replace("Z", "+00:00"))
        if dt.tzinfo is not None:
            dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
    raw_level = payload.get("nivel_agua_cm")
    if raw_level is None:
        raise ValueError("nivel_agua_cm obrigatório")
    level = float(raw_level)
    if not math.isfinite(level) or not (0 <= level <= 10000):
        raise ValueError("nivel_agua_cm inválido")
    level = Decimal(str(level)).quantize(Decimal("0.001"))
    rain_raw = payload.get("chuva_simulada_mm_h")
    rain = float(rain_raw) if rain_raw is not None else 0.0
    if not math.isfinite(rain) or not (0 <= rain <= 200):
        raise ValueError("chuva_simulada_mm_h inválida")
    water_crit = level >= 200
    rain_crit = rain >= 50
    water_attention = level >= 120
    rain_attention = rain >= 25
    if water_crit or rain_crit or (water_attention and rain_attention):
        state = "CRITICO"
    elif water_attention or rain_attention:
        state = "ATENCAO"
    else:
        state = "NORMAL"
    return {
        "id_dispositivo": str(payload.get("id_dispositivo") or os.getenv("DEFAULT_DEVICE_ID", "AVIVA-ESP32-DEMO")),
        "data_hora": dt, "nivel_agua_cm": level, "situacao": state,
        "chuva_simulada_mm_h": payload.get("chuva_simulada_mm_h"),
        "umidade_dht22_pct": payload.get("umidade_dht22_pct"),
    }

# Usa Secrets Manager quando configurado; caso contrário, lê variáveis de ambiente.
def _credentials():
    secret_arn = os.getenv("DB_SECRET_ARN")
    if secret_arn:
        import boto3
        secret = boto3.client("secretsmanager").get_secret_value(SecretId=secret_arn)
        data = json.loads(secret["SecretString"])
        return {"host": data.get("host") or os.environ["DB_HOST"],
                "user": data.get("username") or data.get("user"),
                "password": data["password"], "port": int(data.get("port", 3306)),
                "database": os.getenv("DB_NAME", "aviva_gs_2026")}
    return {"host": os.environ["DB_HOST"], "user": os.environ["DB_USER"],
            "password": os.environ["DB_PASSWORD"],
            "database": os.getenv("DB_NAME", "aviva_gs_2026"),
            "port": int(os.getenv("DB_PORT", "3306"))}

# A chave única de dispositivo e horário evita duplicar medições reenviadas.
def persist(measurement):
    import pymysql
    cfg = _credentials()
    cfg.update(connect_timeout=10, read_timeout=10, write_timeout=10,
               autocommit=False, charset="utf8mb4")
    ca = os.getenv("RDS_CA_BUNDLE")
    if ca:
        cfg["ssl"] = {"ca": ca, "check_hostname": True}
    with pymysql.connect(**cfg) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """INSERT INTO leitura_iot
                  (id_dispositivo, data_hora, nivel_agua_cm, chuva_simulada_mm_h,
                   umidade_dht22_pct, situacao, falha_sensor, natureza)
                   VALUES (%s,%s,%s,%s,%s,%s,NULL,'LEITURA_EXPORTADA')
                   ON DUPLICATE KEY UPDATE id_leitura=LAST_INSERT_ID(id_leitura)""",
                (measurement["id_dispositivo"], measurement["data_hora"],
                 measurement["nivel_agua_cm"], measurement["chuva_simulada_mm_h"],
                 measurement["umidade_dht22_pct"], measurement["situacao"]))
            out = {"id_leitura": cursor.lastrowid, "novo": cursor.rowcount == 1}
        conn.commit()
        return out

# Processa somente eventos de criação de JSON no bucket e prefixo permitidos.
def lambda_handler(event, context):
    import boto3
    s3 = boto3.client("s3")
    expected_bucket = os.getenv("S3_BUCKET")
    prefix = os.getenv("S3_PREFIX", "medicoes/")
    processed = []
    for row in event.get("Records", []):
        if not row.get("eventName", "").startswith("ObjectCreated:"):
            continue
        bucket = row["s3"]["bucket"]["name"]
        key = unquote_plus(row["s3"]["object"]["key"])
        if expected_bucket and bucket != expected_bucket:
            raise ValueError("bucket inesperado")
        if not key.startswith(prefix) or not key.endswith(".json"):
            continue
        raw = s3.get_object(Bucket=bucket, Key=key)["Body"].read()
        if len(raw) > 100_000:
            raise ValueError("JSON acima do limite")
        measurement = parse_measurement(json.loads(raw.decode("utf-8")))
        saved = persist(measurement)
        LOG.info("Medição processada: id=%s situacao=%s novo=%s",
                 saved["id_leitura"], measurement["situacao"], saved["novo"])
        processed.append({"objeto": key, "situacao": measurement["situacao"], **saved})
    return {"statusCode": 200, "body": json.dumps({"processados": len(processed), "itens": processed})}

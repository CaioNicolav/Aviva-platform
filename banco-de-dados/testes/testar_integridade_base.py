"""Verifica a consistência dos arquivos de dados incluídos na distribuição.

Confere quantidades esperadas, unicidade de identificadores, integridade dos
arquivos CNES comprimidos e presença de cargas SQL. Não consulta o MySQL.
"""
from pathlib import Path
import csv
import gzip
import hashlib
import io

ROOT = Path(__file__).resolve().parents[2]
R = ROOT / "modulos/reabilitacao/data"
C = ROOT / "modulos/comunidade/data/processed"


def rows(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def candidates():
    raw = R / "cnes_candidatos.csv"
    if raw.exists():
        return rows(raw)
    parts = sorted(R.glob("cnes_candidatos.csv.gz.part*"))
    assert len(parts) == 5, "Arquivos do CNES incompletos"
    compressed = b"".join(part.read_bytes() for part in parts)
    digest = "44678323a25abaca26d8b4154f7280a7177b6653fbcd48b07b03d5390fb04261"
    assert hashlib.sha256(compressed).hexdigest() == digest, "CNES comprimido corrompido"
    data = gzip.decompress(compressed).decode("utf-8-sig")
    return list(csv.DictReader(io.StringIO(data)))


def main():
    audit = rows(R / "auditoria_integral_sp.csv")
    ubs = rows(R / "ubs_cnes_sp.csv")
    cand = candidates()
    offices = rows(R / "oficinas_documentadas_sp.csv")
    climate = rows(C / "aviva_clima_diario.csv")
    events = rows(C / "eventos_violencia_simulados.csv")
    areas = rows(R / "areas_abrangencia_ubs_2026_resumo.csv")
    sp = {r["cnes"] for r in cand if r["municipio_ibge"] == "355030"} | {r["cnes"] for r in ubs} | {r["cnes"] for r in offices}
    assert len(audit) == 2647 and {r["cnes"] for r in audit} == sp
    assert len({r["cnes"] for r in audit}) == len(audit)
    assert sum(r["mostrar_pin_verificado"] == "SIM" for r in audit) == 448
    assert len(climate) == 604 and len({(r["estacao"], r["data"]) for r in climate}) == 604
    assert len(events) == 4000 and len({r["id_evento"] for r in events}) == 4000
    assert all(r["origem"].lower() == "simulado" for r in events)
    assert len([r for r in areas if r["cnes"] in sp]) == 478
    sql = (ROOT / "banco-de-dados/sql/02_carga_dados.sql").read_text(encoding="utf-8")
    for table in ["estabelecimento_saude", "validacao_localizacao", "clima_diario", "evento_comunitario", "leitura_iot"]:
        assert f"INSERT INTO {table} " in sql
    assert "EXEMPLO_DIDATICO" in sql
    print("OK | 2.647 estabelecimentos, 448 localizações verificadas, 478 UBS, 604 dias, 4.000 eventos SIMULADOS")


if __name__ == "__main__":
    main()

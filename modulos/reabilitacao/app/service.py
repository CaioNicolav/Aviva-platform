"""Consulta registros curados de serviços públicos de reabilitação.

Normaliza termos de pesquisa e filtra serviços por localidade e modalidade.
As informações retornadas dependem da data de referência e da fonte cadastrada.
"""
import csv
import re
import unicodedata
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
DATA_PATH = BASE / "data" / "servicos_validados.csv"
MODALIDADES = ("fisica", "auditiva", "visual", "intelectual")
UFS = frozenset("AC AL AP AM BA CE DF ES GO MA MT MS MG PA PB PR PE PI RJ RN RS RO RR SC SP SE TO".split())


def normalize(value):
    value = unicodedata.normalize("NFKD", str(value or ""))
    return "".join(c for c in value if not unicodedata.combining(c)).strip().casefold()


def load_services(path=DATA_PATH):
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        records = list(csv.DictReader(f, delimiter=","))
    clean = []
    for record in records:
        if not all(record.get(k, "").strip() for k in ("cnes", "nome", "uf", "municipio", "fonte_url", "data_referencia")):
            continue
        if record.get("status_verificacao", "").strip().lower() != "confirmado":
            continue
        if record.get("atende_sus", "").strip().lower() != "sim":
            continue
        if record["uf"].upper() not in UFS:
            continue
        mods = [v.strip().lower() for v in record.get("modalidades", "").split("|") if v.strip()]
        if not mods or any(v not in MODALIDADES for v in mods):
            continue
        # URLs externas são exibidas somente se apontarem para HTTPS.
        if not record["fonte_url"].startswith("https://"):
            continue
        clean.append({
            "cnes": record["cnes"], "nome": record["nome"], "uf": record["uf"].upper(),
            "municipio": record["municipio"], "endereco": record.get("endereco", ""),
            "telefone": record.get("telefone", ""), "modalidades": mods,
            "tipo_unidade": record.get("tipo_unidade", ""), "fonte_url": record["fonte_url"],
            "data_referencia": record["data_referencia"],
            "aviso": "Cadastro conferido, não representa vaga ou atendimento garantido. Confirme com a rede local.",
        })
    return clean


def search_services(uf=None, municipio=None, modalidade=None, records=None):
    if uf and uf.upper() not in UFS:
        raise ValueError("UF inválida. Use a sigla oficial, como SP ou MG.")
    if modalidade and modalidade not in MODALIDADES:
        raise ValueError("Modalidade inválida.")
    if municipio and not re.fullmatch(r"[\w\sÀ-ÿ.'-]{1,90}", municipio, re.UNICODE):
        raise ValueError("Município inválido.")
    services = load_services() if records is None else records
    results = [s for s in services if
               (not uf or s["uf"].upper() == uf.upper()) and
               (not municipio or normalize(municipio) in normalize(s["municipio"])) and
               (not modalidade or modalidade in s["modalidades"])]
    return sorted(results, key=lambda s: (s["uf"], normalize(s["municipio"]), normalize(s["nome"])))

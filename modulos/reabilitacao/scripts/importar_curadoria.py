"""Valida e importa uma planilha CSV previamente conferida contra fontes oficiais.
Uso: python -m scripts.importar_curadoria /caminho/arquivo.csv
NÃO consulta a API do CNES nem presume habilitações de reabilitação.
"""
import csv
import shutil
import sys
from pathlib import Path
from app.service import DATA_PATH, MODALIDADES, UFS

EXPECTED = ["cnes", "nome", "uf", "municipio", "endereco", "telefone", "tipo_unidade", "modalidades", "atende_sus", "fonte_url", "data_referencia", "status_verificacao"]


def validate(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames != EXPECTED:
            raise ValueError(f"Colunas esperadas, nessa ordem: {', '.join(EXPECTED)}")
        rows = list(reader)
    if not rows:
        raise ValueError("Arquivo vazio: nenhuma unidade para importar.")
    ids = set()
    for i, row in enumerate(rows, start=2):
        if not row["cnes"].strip().isdigit():
            raise ValueError(f"Linha {i}: CNES inválido.")
        if row["cnes"] in ids:
            raise ValueError(f"Linha {i}: CNES duplicado.")
        ids.add(row["cnes"])
        if not all(row.get(k, "").strip() for k in ("nome", "municipio", "data_referencia", "fonte_url")):
            raise ValueError(f"Linha {i}: falta nome, município, referência ou fonte.")
        if row["uf"].upper() not in UFS:
            raise ValueError(f"Linha {i}: UF inválida.")
        mods = row["modalidades"].split("|")
        if any(m not in MODALIDADES for m in mods):
            raise ValueError(f"Linha {i}: modalidade não oficial.")
        if row["atende_sus"].lower() != "sim" or row["status_verificacao"].lower() != "confirmado":
            raise ValueError(f"Linha {i}: somente registros com SUS e habilitação conferidos.")
        if not row["fonte_url"].startswith("https://"):
            raise ValueError(f"Linha {i}: fonte HTTPS obrigatória.")
    return len(rows)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Uso: python -m scripts.importar_curadoria entrada.csv")
    count = validate(sys.argv[1])
    shutil.copyfile(sys.argv[1], DATA_PATH)
    print(f"Importados {count} registros conferidos em {DATA_PATH}")

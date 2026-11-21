"""Atualiza nomes de municípios com base em códigos do IBGE.

Com internet: `py -m scripts.atualizar_municipios` usa API pública do IBGE.
Ou: `py -m scripts.atualizar_municipios municipios.csv` usando CSV de duas colunas
`codigo_ibge,nome` (7 ou 6 dígitos de código).

A rotina trabalha no CSV local e preserva o ZIP original do CNES.
"""
import csv
import json
import sys
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
TARGET = BASE / 'data' / 'cnes_candidatos.csv'
IBGE_API = 'https://servicodados.ibge.gov.br/api/v1/localidades/municipios'


def load_ibge_map(path=None):
    if path:
        with Path(path).open(encoding='utf-8-sig', newline='') as f:
            raw = list(csv.DictReader(f))
        return {str(item['codigo_ibge']).strip()[:6]: str(item['nome']).strip() for item in raw if item.get('codigo_ibge') and item.get('nome')}
    request = urllib.request.Request(IBGE_API, headers={'User-Agent': 'AVIVA-Projeto-Academico/0.2'})
    with urllib.request.urlopen(request, timeout=30) as f:
        raw = json.load(f)
    return {str(item['id'])[:6]: str(item['nome']).strip() for item in raw}


def main():
    names = load_ibge_map(sys.argv[1] if len(sys.argv) > 1 else None)
    with TARGET.open(encoding='utf-8-sig', newline='') as f:
        reader=csv.DictReader(f)
        columns=reader.fieldnames
        records=list(reader)
    matched=0
    for row in records:
        label=names.get(row['municipio_ibge'])
        if label:
            row['municipio']=label
            matched+=1
    tmp=TARGET.with_suffix('.tmp')
    with tmp.open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=columns)
        writer.writeheader(); writer.writerows(records)
    tmp.replace(TARGET)
    print(f'Enriquecidos {matched} de {len(records)} registros com nomes de municípios. Reinicie o servidor.')

if __name__=='__main__':
    main()

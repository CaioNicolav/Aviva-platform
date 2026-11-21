"""Auditoria geográfica exploratória de pontos da capital paulista.

APLICAÇÃO:
- Corrige erros pontuais com origem/referência explícita.
- Rejeita COORDENADAS com discrepância extrema em relação ao agrupamento
  de cadastros do mesmo bairro (heurística, não atestado de precisão).
- Preserva dados brutos do CNES sem sobrescrever a fonte original.
NÃO ESTÁ GARANTIDO que os demais pins representam a posição exata.
"""
from functools import lru_cache
from math import isfinite, radians, sin, cos, asin, sqrt
from statistics import median
from csv import DictReader
from pathlib import Path
from collections import defaultdict
from .cnes_exploratorio import registros_consulta
from .service import normalize

ROOT=Path(__file__).resolve().parents[1]
CORRECOES=ROOT/'data'/'correcoes_geo_sp.csv'
LIMIAR_KM=6.0
MIN_AMOSTRA_BAIRRO=5

def distancia_km(lat1,lon1,lat2,lon2):
    p1,p2 = radians(lat1),radians(lat2)
    d1,d2=radians(lat2-lat1),radians(lon2-lon1)
    h=sin(d1/2)**2+cos(p1)*cos(p2)*sin(d2/2)**2
    return 2*6371.0088*asin(min(1,sqrt(h)))

def coordenada_cnes(r):
    try:
        lat,lon=float(r.get('latitude','')),float(r.get('longitude',''))
    except (ValueError,TypeError): return None
    if not (isfinite(lat) and isfinite(lon)): return None
    if not (-24.10<=lat<=-23.25 and -47.20<=lon<=-46.25): return None
    return lat,lon

@lru_cache(maxsize=1)
def auditoria_sp():
    """Retorna ID CNES -> registro da auditoria; um único passe cached por processo."""
    registros=[r for r in registros_consulta() if r.get('uf')=='SP' and r.get('municipio_ibge')=='355030']
    pontos=defaultdict(list)
    for r in registros:
        par=coordenada_cnes(r)
        bairro=normalize(r.get('bairro',''))
        if par and bairro:pontos[bairro].append(par)
    referencias={b:(median([x[0] for x in vals]),median([x[1] for x in vals]),len(vals))
                 for b, vals in pontos.items() if len(vals)>=MIN_AMOSTRA_BAIRRO}
    correcoes={}
    if CORRECOES.exists():
        with CORRECOES.open(encoding='utf-8-sig',newline='') as f:
            correcoes={r['cnes']:r for r in DictReader(f)}
    result={}
    for r in registros:
        cnes=r['cnes']
        latlon=coordenada_cnes(r)
        correcao=correcoes.get(cnes)
        if correcao:
            par=(float(correcao['latitude']),float(correcao['longitude']))
            if coordenada_cnes({'latitude':par[0],'longitude':par[1]}) is None:continue
            result[cnes]={'coordenadas':par,'status':'revisao_endereco_fonte_externa',
                          'fonte_coordenada':correcao['fonte_coordenada'],
                          'observacao':correcao['observacao'],'distancia_bairro_km':None}
            continue
        if latlon is None:
            result[cnes]={'coordenadas':None,'status':'sem_coordenadas','observacao':'Sem coordenadas utilizáveis no cadastro.','distancia_bairro_km':None}
            continue
        ref=referencias.get(normalize(r.get('bairro','')))
        if ref:
            dist=distancia_km(*latlon,ref[0],ref[1])
            if dist>LIMIAR_KM:
                result[cnes]={'coordenadas':None,'status':'inconsistencia_geografica_suspeita',
                              'observacao':('Coordenadas CNES omitidas do mapa: distância de %.1f km '
                                            'do agrupamento cadastral do mesmo bairro. Necessária revisão por endereço.' % dist),
                              'distancia_bairro_km':round(dist,2)}
                continue
            result[cnes]={'coordenadas':latlon,'status':'coerente_com_agrupamento_bairro_nao_verificado',
                          'observacao':'Posição cadastral preliminar, coerente com agrupamento do bairro. NÃO validada por geocodificação do endereço.',
                          'distancia_bairro_km':round(dist,2)}
        else:
            result[cnes]={'coordenadas':latlon,'status':'nao_auditada_sem_referencia_bairro',
                          'observacao':'Posição cadastral preliminar; bairro com poucos pontos para testar consistência. CONFIRME o endereço antes de ir.',
                          'distancia_bairro_km':None}
    return result

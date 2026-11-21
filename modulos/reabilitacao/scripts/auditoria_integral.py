"""AVIVA | Auditoria geográfica de cadastros de estabelecimentos em São Paulo.
Compara pontos com referências externas sem presumir validade de endereços não verificados.
"""
from __future__ import annotations
import argparse,csv,json,math,os,re,statistics,unicodedata,zipfile
from collections import Counter,defaultdict
from datetime import date
from pathlib import Path
from difflib import SequenceMatcher
from xml.etree import ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'
BBOX=(-24.10,-23.25,-47.20,-46.25)
URL_GEOSAMPA='https://metadados.geosampa.prefeitura.sp.gov.br/geonetwork/srv/api/records/bc44ee6c-e973-4670-b912-9ac8d64b9f56'

def norm(s):
    s=unicodedata.normalize('NFKD',str(s or ''))
    s=''.join(c for c in s if not unicodedata.combining(c)).upper()
    return re.sub(r'[^A-Z0-9]+',' ',s).strip()

def rowval(r,*names):
    low={norm(k).replace(' ',''):v for k,v in r.items()}
    for n in names:
        v=low.get(norm(n).replace(' ',''))
        if v is not None and str(v).strip():return str(v).strip()
    return ''

def readcsv(path):
    with path.open(encoding='utf-8-sig',newline='') as f: return list(csv.DictReader(f))

def parsefloat(s):
    try: v=float(str(s).strip().replace(',','.'))
    except (ValueError,TypeError):return None
    return v if math.isfinite(v) else None

def coord(r):
    la=parsefloat(rowval(r,'latitude','lat','LATITUDE','LAT'))
    lo=parsefloat(rowval(r,'longitude','lon','lng','LONGITUDE','LONG'))
    if la is None or lo is None:return None
    if not (BBOX[0]<=la<=BBOX[1] and BBOX[2]<=lo<=BBOX[3]):return None
    return (la,lo)

def hav(a,b):
    la1,lo1=a;la2,lo2=b
    rad=math.pi/180
    h=math.sin((la2-la1)*rad/2)**2+math.cos(la1*rad)*math.cos(la2*rad)*math.sin((lo2-lo1)*rad/2)**2
    return 12742.0176*math.asin(min(1,math.sqrt(h)))

def cep(r):return re.sub(r'\D','',r.get('cep',''))

def numero(r):
    endereco=norm(r.get('endereco',''))
    mm=re.search(r'\b([0-9]{1,5})\s*$',endereco)
    return mm.group(1) if mm else ''

def street(r):
    e=norm(r.get('endereco',''))
    e=re.sub(r'\b(?:RUA|R|AVENIDA|AV|PRACA|PCA|ESTRADA|EST|TRAVESSA|TV|ALAMEDA|AL)\b',' ',e)
    e=re.sub(r'\b(?:S N|SN|SEM NUMERO|N|NRO|NUMERO)\b',' ',e)
    e=re.sub(r'\b\d{1,5}\s*$',' ',e)
    return re.sub(r'\s+',' ',e).strip()

def read_records():
    allr=[]; known=set()
    for f in ['cnes_candidatos.csv','oficinas_documentadas_sp.csv','ubs_cnes_sp.csv']:
        for r in readcsv(DATA/f):
            if r.get('uf')=='SP' and r.get('municipio_ibge')=='355030' and r['cnes'] not in known:
                allr.append(r);known.add(r['cnes'])
    return sorted(allr,key=lambda x:(x.get('categoria_indicio_nome',''),x.get('nome',''),x['cnes']))

def get_polygon_coordinates_geojson(path):
    j=json.loads(path.read_text(encoding='utf-8-sig'))
    features=j.get('features',[]) if isinstance(j,dict) else []
    for f in features:
        prop=f.get('properties') or {}
        geom=f.get('geometry') or {}
        if geom.get('type')!='Point':continue
        coords=geom.get('coordinates') or []
        if len(coords)<2: continue
        row={str(k):str(v) if v is not None else '' for k,v in prop.items()}
        row['latitude']=str(coords[1]);row['longitude']=str(coords[0])
        yield row

def kml_elements(content):
    root=ET.fromstring(content)
    for p in root.iter():
        if p.tag.rsplit('}',1)[-1]!='Placemark':continue
        row={}
        for ch in p.iter():
            tag=ch.tag.rsplit('}',1)[-1]
            if tag=='name' and 'nome' not in row and ch.text:row['nome']=ch.text.strip()
            if tag=='SimpleData' and ch.get('name'):row[ch.get('name')]=ch.text or ''
            if tag=='Data' and ch.get('name'):
                v=next((e for e in ch if e.tag.rsplit('}',1)[-1]=='value'),None)
                if v is not None:row[ch.get('name')]=v.text or ''
            if tag=='coordinates' and ch.text and ch.text.strip():
                if any(e.tag.rsplit('}',1)[-1]=='Point' for e in p.iter()):
                    first=ch.text.strip().split()[0].split(',')
                    if len(first)>=2:row['longitude'],row['latitude']=first[:2]
        if 'latitude' in row:yield row

def load_reference(path):
    if not path:return []
    path=Path(path)
    ext=path.suffix.lower()
    if ext=='.csv':return readcsv(path)
    if ext in ('.geojson','.json'):return list(get_polygon_coordinates_geojson(path))
    if ext=='.kml':return list(kml_elements(path.read_bytes()))
    if ext=='.kmz':
        with zipfile.ZipFile(path) as z:
            files=[x for x in z.namelist() if x.lower().endswith('.kml')]
            if not files:raise ValueError('KMZ sem KML interno')
            return list(kml_elements(z.read(files[0])))
    raise ValueError('A referência deve ser .csv, .geojson, .kml ou .kmz')

def match_references(registros,refs):
    """Only exact unique ID or conservative unique NAME+STREET+NUMBER.
    A name alone never validates an address.
    """
    byid=defaultdict(list);bykey=defaultdict(list)
    for r in refs:
        xy=coord(r)
        if not xy:continue
        c=rowval(r,'cnes','co_cnes','codigo_cnes','cnese','codigo cnes')
        if c:byid[re.sub(r'\D','',c)].append((r,xy))
        nr=norm(rowval(r,'nome','no_fantasia','nome_fantasia','nome_estabelecimento','nm_equipamento','estabelecimento'))
        er=rowval(r,'endereco','logradouro','ds_endereco','endereco_completo','no_logradouro')
        if er:
            fake={'endereco':er}; key=(nr,street(fake),numero(fake))
            if all(key):bykey[key].append((r,xy))
    matched={}
    for r in registros:
        cid=re.sub(r'\D','',r['cnes']); cands=byid.get(cid,[])
        method='identificador_cnes'
        if len(cands)!=1:
            key=(norm(r['nome']),street(r),numero(r))
            cands=bykey.get(key,[]) if all(key) else []
            method='nome_logradouro_numero_exatos'
        if len(cands)==1:
            rr,xy=cands[0]
            matched[r['cnes']]={'coordenada_referencia':xy,'metodo':method,'referencia_nome':rowval(rr,'nome','nome_fantasia','no_fantasia','nome_estabelecimento','nm_equipamento'),'referencia_endereco':rowval(rr,'endereco','logradouro','ds_endereco','endereco_completo')}
    return matched

def med(pairs):return statistics.median(x[0] for x in pairs),statistics.median(x[1] for x in pairs)

def group_reference(records,keyfn,minn=5,maxsp=3.0):
    group=defaultdict(list)
    for r in records:
        xy=coord(r)
        key=keyfn(r)
        if key and xy:group[key].append(xy)
    stable={}
    for k,coords in group.items():
        if len(coords)<minn:continue
        m=med(coords)
        d=[hav(x,m) for x in coords]
        if statistics.median(d)<=maxsp:stable[k]=(m,len(coords))
    return stable

def audit(records,official):
    bairros=group_reference(records,lambda r:norm(r.get('bairro','')),minn=5,maxsp=2.0)
    ceps=group_reference(records,lambda r:cep(r)[:5] if len(cep(r))==8 else '',minn=4,maxsp=2.0)
    duplicates=defaultdict(list)
    for r in records:
        xy=coord(r)
        if xy:duplicates[tuple(round(x,5) for x in xy)].append(r)
    auditrows=[]
    for r in records:
        xy=coord(r);flags=[]
        if not xy:flags.append('coordenada_ausente_ou_fora_da_area_ampla')
        if len(cep(r))!=8:flags.append('cep_ausente_ou_invalido')
        if not street(r):flags.append('logradouro_ausente')
        if not numero(r):flags.append('numero_ausente_ou_s_n')
        if not r.get('bairro','').strip():flags.append('bairro_ausente')
        d_bairro=d_cep=''
        if xy:
            br=bairros.get(norm(r.get('bairro','')))
            if br:
                d_bairro=round(hav(xy,br[0]),2)
                if d_bairro>6:flags.append('coordenada_diverge_agrupamento_bairro')
            cr=ceps.get(cep(r)[:5])
            if cr:
                d_cep=round(hav(xy,cr[0]),2)
                if d_cep>6:flags.append('coordenada_diverge_agrupamento_cep5')
            peers=duplicates[tuple(round(x,5) for x in xy)]
            if len(peers)>=3 and len({cep(v)[:5] for v in peers if len(cep(v))==8})>=3:
                flags.append('coordenada_repetida_entre_ceps_distintos')
        ext=official.get(r['cnes'])
        lat_ref=lon_ref='';desloc='';metodo=''
        if ext:
            lat_ref,lon_ref=ext['coordenada_referencia']
            metodo=ext['metodo']
            if xy:
                desloc=round(hav(xy,(lat_ref,lon_ref)),2)
                if desloc>0.3:flags.append('cnes_diverge_referencia_externa_mais_300m')
            status='ponto_correspondente_referencia_externa'
            pin='SIM'
            pos=(lat_ref,lon_ref)
        elif not xy:
            status='sem_coordenadas_confiaveis';pin='NAO';pos=(None,None)
        elif any(x in flags for x in ['coordenada_diverge_agrupamento_bairro','coordenada_diverge_agrupamento_cep5','coordenada_repetida_entre_ceps_distintos']):
            status='suspeita_automatica_sem_referencia_externa';pin='NAO';pos=(None,None)
        else:
            status='pendente_validacao_em_fonte_externa';pin='NAO';pos=(None,None)
        auditrows.append({
           'cnes':r['cnes'],'categoria':r['categoria_indicio_nome'],'nome':r['nome'],
           'endereco_cnes':r['endereco'],'bairro_cnes':r.get('bairro',''),
           'cep_cnes':r.get('cep',''),'numero_extraido':numero(r),'ambulatorial_sus':r.get('ambulatorial_sus_informado',''),
           'latitude_cnes':r.get('latitude',''),'longitude_cnes':r.get('longitude',''),
           'dist_bairro_mediana_km':d_bairro,'dist_cep5_mediana_km':d_cep,
           'latitude_ref':lat_ref,'longitude_ref':lon_ref,'dist_cnes_referencia_km':desloc,
           'metodo_correspondencia':metodo,'status_auditoria':status,
           'mostrar_pin_verificado':pin,'latitude_pin':pos[0] if pos[0] is not None else '',
           'longitude_pin':pos[1] if pos[1] is not None else '',
           'alertas':';'.join(flags),'caminho_verificacao':'A conferência por fonte independente ainda não foi possível' if not ext else 'Ponto cadastrado em referência externa; confirmar acesso e atendimento',
        })
    return auditrows

def writecsv(path,rows):
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        if not rows:return
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys()));w.writeheader();w.writerows(rows)

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument('--referencia',help='Arquivo oficial de pontos: CSV, GeoJSON, KML ou KMZ')
    p.add_argument('--fonte-url',help='URL do órgão que publicou a referência (para trilha de auditoria)')
    args=p.parse_args(argv)
    if args.referencia and args.referencia.lower().endswith(('.kmz','.kml')):
        raise SystemExit('AVIVA 0.10: não reexecute o importador legado diretamente com KMZ/KML; isso perderia as validações de endereço. Use o cruzamento em data/cruzamento_enderecos_ubs_2026.csv e o relatório v10.')
    rows=read_records()
    ref=load_reference(args.referencia)
    matched=match_references(rows,ref)
    audited=audit(rows,matched)
    writecsv(DATA/'auditoria_integral_sp.csv',audited)
    counts=Counter(r['status_auditoria'] for r in audited)
    selected=[r for r in audited if r['ambulatorial_sus']=='SIM']
    selected_counts=Counter(r['status_auditoria'] for r in selected)
    summary={
      'data_execucao':date.today().isoformat(),
      'escopo':'Todos os cadastros carregados no AVIVA com município IBGE 355030 / São Paulo (capital)',
      'total_avaliados':len(audited),'total_no_filtro_sus_ambulatorial':len(selected),
      'categorias':dict(Counter(r['categoria'] for r in audited)),
      'status_todos':dict(counts),'status_subset_app':dict(selected_counts),
      'referencia_externa_registros_carregados':len(ref),
      'referencia_externa_matches_unicos':len(matched),
      'fonte_externa_url':args.fonte_url or '',
      'fonte_externa_arquivo':Path(args.referencia).name if args.referencia else '',
      'referencia_municipal_disponivel':bool(args.referencia),
      'validacao_integral_individual':False,
      'ressalva':'Auditoria automatizada de todos os cadastros não equivale à validação individual de endereços. Confirmar via GeoSampa e cadastro municipal antes de encaminhar cidadãos.'
    }
    (DATA/'resumo_auditoria_integral_sp.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
    doc=ROOT/'docs'/'AUDITORIA_INTEGRAL_SP_v09.md'
    doc.write_text(f'''# AVIVA — Auditoria integral dos registros geográficos de São Paulo

**Data:** {summary['data_execucao']}  
**Escopo analisado:** {len(audited):,} estabelecimentos CNES únicos no recorte de São Paulo, incluindo **{len(selected):,}** com indicação ambulatorial SUS = SIM (filtro padrão do mapa).

## Resultado da varredura automatizada

| Situação da localização | Todos os cadastros | Registros do filtro ambulatorial SUS |
|---|---:|---:|
'''+''.join(f"| {k} | {counts.get(k,0)} | {selected_counts.get(k,0)} |\n" for k in ['ponto_correspondente_referencia_externa','suspeita_automatica_sem_referencia_externa','sem_coordenadas_confiaveis','pendente_validacao_em_fonte_externa'])+f'''

A revisão automatizada percorreu **100% dos {len(audited)} registros** do recorte carregado na versão. Isso **NÃO** é validação cartográfica individual: ela exigiria localizar cada estabelecimento em fonte geográfica independente, conferir endereço/CEP/numeração e, para uso assistencial, confirmar funcionamento e condições atuais de atendimento. O arquivo externo não foi importado nesta execução: **{'SIM' if args.referencia else 'NÃO'}**.

## O que foi verificado para cada registro
- Código CNES único, nome, categoria, endereço e bairro informados no cadastro, CEP e presença de número.
- Coordenadas sintaticamente válidas e dentro de uma área ampla do município.
- Distância ao agrupamento dos registros do mesmo bairro e prefixo CEP-5, apenas quando há amostras suficientes e coesas.
- Duplicidade de coordenadas arredondadas entre estabelecimentos de CEPs diferentes.
- Correspondência contra base cartográfica externa **somente quando um arquivo de referência for fornecido**; preferir correspondência exata de CNES ou correspondência única de nome+logradouro+número.

## Limitações e política do AVIVA
- Bairros e CEPs repetidos, deslocados ou inconsistentes podem não ser detectados por verificações estatísticas.
- Coordenadas coerentes com pontos próximos do CNES **não comprovam posição correta**; dados com o mesmo erro podem formar um agrupamento coerente.
- Coordenadas substituídas por referências secundárias, como a UBS Boracea na versão 0.8, **não são consideradas confirmação oficial**.
- Pontos sem referência geográfica independente **não devem ser usados em roteamento nem na função ‘mais próximos’ como opções confiáveis**.
- O CNES não assegura disponibilidade de atendimento, habilitação em reabilitação, horários ou vagas.

## Fonte oficial para próxima etapa
Metadados da camada municipal UBS/Posto/Centro de Saúde: {URL_GEOSAMPA}

Página da Prefeitura com **Estabelecimentos de Referência das Áreas de Abrangência 2026**: https://prefeitura.sp.gov.br/web/saude/w/epidemiologia_e_informacao/geoprocessamento_e_informacoes_socioambientais/265388

## Como efetuar cruzamento externo e repetir auditoria
1. Baixe a camada oficial em **KMZ/KML ou CSV/GeoJSON com lat/lon em WGS84**; não utilize imagem do mapa nem uma lista sem coordenadas.
2. Coloque o arquivo na pasta `data/`.
3. Execute: `py -m scripts.auditoria_integral --referencia "data/NOME_ARQUIVO.kmz" --fonte-url "URL_DA_FONTE"`.
4. Leia `data/resumo_auditoria_integral_sp.json` e `data/auditoria_integral_sp.csv`.
5. Reabra o servidor. Só os **pontos correspondentes à fonte independente** serão elegíveis à funcionalidade de proximidade na versão 0.9.

**Não é correto afirmar que todos os endereços foram validados.** Os casos pendentes permanecem disponíveis na pesquisa textual, com avisos para conferir a fonte oficial.
''',encoding='utf8')
    print(json.dumps(summary,indent=2,ensure_ascii=False))
    return summary

if __name__=='__main__':main()

"""AVIVA | Pesquisa exploratória de estabelecimentos cadastrados no CNES.
Cadastros encontrados não comprovam modalidade, habilitação ou disponibilidade.
"""
import csv
import re
from functools import lru_cache
from pathlib import Path
from .service import UFS, normalize
from .territorio_sp import ZONAS, zona_do_bairro

DATA_PATH = Path(__file__).resolve().parents[1] / 'data' / 'cnes_candidatos.csv'
OFICINAS_PATH = Path(__file__).resolve().parents[1] / 'data' / 'oficinas_documentadas_sp.csv'
UBS_PATH = Path(__file__).resolve().parents[1] / 'data' / 'ubs_cnes_sp.csv'
CATEGORIAS = {'CAPS','CER','OUTROS','OFICINA','UBS'}

@lru_cache(maxsize=1)
def load_candidates():
    if DATA_PATH.exists():
        with DATA_PATH.open(encoding='utf-8-sig', newline='') as f:
            return list(csv.DictReader(f))
    import gzip
    import hashlib
    import io
    parts = sorted(DATA_PATH.parent.glob('cnes_candidatos.csv.gz.part*'))
    if not parts:
        return []
    compressed = b''.join(path.read_bytes() for path in parts)
    expected = '44678323a25abaca26d8b4154f7280a7177b6653fbcd48b07b03d5390fb04261'
    if hashlib.sha256(compressed).hexdigest() != expected:
        raise RuntimeError('Base CNES pública incompleta ou com integridade inválida')
    raw = gzip.decompress(compressed).decode('utf-8-sig')
    return list(csv.DictReader(io.StringIO(raw)))


@lru_cache(maxsize=1)
def load_documented_offices():
    """Oficinas com documentação institucional, NÃO confirmação de vagas/SUS em tempo real."""
    if not OFICINAS_PATH.exists():
        return []
    with OFICINAS_PATH.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


@lru_cache(maxsize=1)
def load_ubs_sp():
    """UBS na capital: código de tipo cadastral 2 + nome compatível + SUS ambulatorial SIM.

    NÃO comprova reabilitação especializada no local, vagas nem UBS de referência.
    """
    if not UBS_PATH.exists():
        return []
    with UBS_PATH.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


@lru_cache(maxsize=1)
def registros_consulta():
    """Agrega cadastros sem duplicar CNES nem reclassificar outras categorias."""
    originals = load_candidates()
    all_records = list(originals)
    known = {r['cnes'] for r in originals}
    for source in (load_documented_offices(),load_ubs_sp()):
        for row in source:
            if row['cnes'] not in known:
                all_records.append(row)
                known.add(row['cnes'])
    return all_records


def search_candidates(uf=None, municipio=None, categoria=None, limite=30, pagina=1, somente_ambulatorial_sus=True, zona=None, bairro=None):
    if uf and uf.upper() not in UFS:
        raise ValueError('UF inválida')
    if categoria and categoria not in CATEGORIAS:
        raise ValueError('Categoria inválida; use UBS, CAPS, CER, OUTROS ou OFICINA')
    if zona and zona not in ZONAS:
        raise ValueError('Zona inválida')
    if bairro and not re.fullmatch(r"[\w\sÀ-ÿ.'-]{1,100}", bairro, re.UNICODE):
        raise ValueError('Bairro inválido')
    if (zona or bairro) and (uf != 'SP' or normalize(municipio) not in ('sao paulo', '355030', '3550308')):
        raise ValueError('Filtro por zona ou bairro disponível apenas para a cidade de São Paulo (SP)')
    if municipio and not re.fullmatch(r"[\w\sÀ-ÿ.'-]{1,90}", municipio, re.UNICODE):
        raise ValueError('Município inválido; digite nome ou código IBGE de seis dígitos')
    if not (1 <= limite <= 100):
        raise ValueError('Limite inválido')
    if not (1 <= pagina <= 10000):
        raise ValueError('Página inválida')
    query = normalize(municipio)
    def matches(s):
        if uf and s['uf'] != uf.upper(): return False
        if categoria and s['categoria_indicio_nome'] != categoria: return False
        if somente_ambulatorial_sus and s['ambulatorial_sus_informado'] != 'SIM': return False
        if query and not (query in normalize(s['municipio']) or query == s['municipio_ibge'] or query == '3550308' and s['municipio_ibge'] == '355030'): return False
        if bairro and normalize(s['bairro']) != normalize(bairro): return False
        if zona and zona_do_bairro(s['bairro']) != zona: return False
        return True
    found = [r for r in registros_consulta() if matches(r)]
    found.sort(key=lambda r:(r['uf'],r['municipio_ibge'],r['categoria_indicio_nome'], normalize(r['nome'])))
    from .geografia import audit_rows
    auditoria_atual=audit_rows()
    start=(pagina-1)*limite
    selected=found[start:start+limite]
    return {'total':len(found),'limite':limite,'pagina':pagina, 'resultados':[
        {'cnes':r['cnes'], 'nome':r['nome'],'uf':r['uf'], 'municipio':r['municipio'] or f"Código IBGE {r['municipio_ibge']}",
         'municipio_ibge':r['municipio_ibge'], 'endereco':r['endereco'], 'bairro':r['bairro'], 'telefone':r['telefone'],
         'categoria_indicio_nome':r['categoria_indicio_nome'], 'ambulatorial_sus_informado':r['ambulatorial_sus_informado'],
         'tipo_unidade_codigo':r.get('tipo_unidade_codigo',''),
         'status_localizacao': auditoria_atual.get(r['cnes'],{}).get('status_auditoria','pendente_validacao_em_fonte_externa'),
         'alertas_localizacao': auditoria_atual.get(r['cnes'],{}).get('alertas',''),
         'zona_preliminar':zona_do_bairro(r['bairro']) if r['uf']=='SP' and r['municipio_ibge']=='355030' else None,
         'fonte_url':r['fonte_url'], 'status_verificacao':r.get('status_verificacao','pendente'), 'tipo_fonte':r.get('tipo_fonte','indicio_nome_cnes'),
         'acesso':r.get('acesso',''), 'observacao_localizacao':r.get('observacao_localizacao',''),
         'aviso': ('Oficina documentada por fonte institucional. A existência do serviço não garante acesso pelo SUS, agenda, habilitação atual ou vaga. Confirme antes de ir.' if r.get('tipo_fonte')=='institucional_documentado' else
                   'UBS identificada pelo tipo cadastral 2 e nome no CNES. Isso NÃO confirma reabilitação especializada, horário, vagas nem que seja sua UBS de referência. Confirme com a rede municipal.' if r.get('tipo_fonte')=='cnes_tipo_unidade_ubs' else
                   'Registro oficial do CNES. A categoria é uma pista pelo nome, NÃO prova habilitação, modalidade, atendimento ou disponibilidade. Consulte UBS/Secretaria de Saúde.')}
        for r in selected
    ]}


def bairros_disponiveis_sp(zona=None, categoria=None):
    """Bairros literalmente registrados no CNES, em São Paulo capital."""
    if zona and zona not in ZONAS:
        raise ValueError('Zona inválida')
    if categoria and categoria not in CATEGORIAS:
        raise ValueError('Categoria inválida')
    records = [r for r in registros_consulta() if r['uf'] == 'SP'
               and r['municipio_ibge'] == '355030'
               and r['ambulatorial_sus_informado'] == 'SIM'
               and (not zona or zona_do_bairro(r['bairro']) == zona)
               and (not categoria or r['categoria_indicio_nome'] == categoria)]
    bairros = sorted({r['bairro'].strip() for r in records if r['bairro'].strip()}, key=normalize)
    return {'municipio':'São Paulo', 'uf':'SP', 'total_bairros':len(bairros),
            'bairros':bairros, 'zonas':[{'id':i, 'titulo':nome} for i,nome in ZONAS.items()],
            'aviso': 'Bairros são texto do CNES. A zona é uma classificação preliminar e conservadora; registros sem associação clara permanecem sem zona identificada.'}

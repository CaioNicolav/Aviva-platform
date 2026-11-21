"""AVIVA | Preparação dos pontos do mapa de serviços de reabilitação.
Distingue posições verificadas de dados históricos e coordenadas não confirmadas.
"""
import csv
import json
from functools import lru_cache
from pathlib import Path

from .auditoria_geo import coordenada_cnes
from .cnes_exploratorio import CATEGORIAS, registros_consulta
from .service import normalize
from .territorio_sp import ZONAS, zona_do_bairro

DATA = Path(__file__).resolve().parents[1] / 'data'


@lru_cache(maxsize=1)
def audit_rows():
    path = DATA / 'auditoria_integral_sp.csv'
    if not path.exists():
        return {}
    with path.open(encoding='utf-8-sig', newline='') as f:
        return {r['cnes']: r for r in csv.DictReader(f)}


@lru_cache(maxsize=1)
def audit_summary():
    path = DATA / 'resumo_auditoria_integral_sp.json'
    return json.loads(path.read_text(encoding='utf8')) if path.exists() else {}


def coordenadas_sp(r):
    """Confirma somente formato e limites gerais da capital; NÃO valida endereço."""
    return coordenada_cnes(r)


@lru_cache(maxsize=1)
def official_addresses():
    path = DATA / 'referencia_municipal_ubs_2026.csv'
    if not path.exists():
        return {}
    with path.open(encoding='utf-8-sig', newline='') as f:
        return {r['cnes']: r for r in csv.DictReader(f)}


@lru_cache(maxsize=1)
def referencias_historicas_2024():
    """Recorte pesquisado de 2024: serve apenas como pista, não prova atual."""
    path = DATA / 'referencia_municipal_historica_2024_auditoria.csv'
    if not path.exists():
        return {}
    with path.open(encoding='utf-8-sig', newline='') as f:
        return {r['cnes']: r for r in csv.DictReader(f)}


def _coordenadas_historicas_se_compativeis(ref):
    if not ref or ref.get('correspondencia_2024') != 'COMPATIVEL_2024_RUA_NUMERO_CEP':
        return None
    return coordenada_cnes({'latitude': ref.get('latitude_municipal_2024'),
                            'longitude': ref.get('longitude_municipal_2024')})


def _descricao_pin(r, a, ref):
    """Uma saída contém os dois níveis distintos: localização e serviço.

    A confirmação do endereço por duas fontes jamais confirma operação atual.
    """
    status = a.get('status_auditoria', 'pendente_validacao_em_fonte_externa')
    verificado = status == 'ponto_correspondente_referencia_externa' and r['categoria_indicio_nome'] == 'UBS'
    tipo = r.get('tipo_fonte', '')
    cadastro = coordenadas_sp(r)
    coords = None
    fonte = 'CNES (coordenada cadastral, não validada)'
    endereco = r['endereco']
    fonte_url = r.get('fonte_url', '')
    origem = 'cnes_sem_verificacao'
    observacao = r.get('observacao_localizacao', '')

    if verificado:
        try:
            coords = (float(a['latitude_pin']), float(a['longitude_pin']))
            if coordenadas_sp({'latitude': coords[0], 'longitude': coords[1]}) is None:
                coords = None
        except (ValueError, TypeError, KeyError):
            coords = None
        if coords:
            endereco = official_addresses().get(r['cnes'], {}).get('endereco_oficial') or endereco
            origem = 'prefeitura_2026_endereco_compativel'
            fonte = 'Prefeitura de São Paulo, AAUBS 2026, e CNES'
            fonte_url = audit_summary().get('fonte_externa_url', '') or fonte_url
    if coords is None:
        coords = cadastro
        if coords is None:
            historico = _coordenadas_historicas_se_compativeis(ref)
            if historico is not None:
                coords = historico
                origem = 'prefeitura_2024_referencia_historica'
                fonte = 'Prefeitura de São Paulo, referência histórica de 2024 (não atualizada)'
        elif ref.get('correspondencia_2024') == 'COMPATIVEL_2024_RUA_NUMERO_CEP':
            origem = 'cnes_com_correspondencia_historica_2024'
    if verificado and origem != 'prefeitura_2026_endereco_compativel':
        verificado = False

    if verificado:
        aviso = ('Endereço conciliado entre CNES e Prefeitura (2026). '
                 'A existência de atendimento ativo, horários, especialidades e vagas NÃO foi confirmada. Confirme antes de ir.')
    elif tipo == 'institucional_documentado':
        aviso = ('ATENÇÃO: existe documentação institucional da oficina, mas o endereço exato do serviço, '
                 'seu funcionamento atual e as condições de atendimento pelo SUS NÃO foram confirmados. '
                 'O ponto pode corresponder ao estabelecimento principal.')
    elif status == 'divergencia_endereco_entre_fontes':
        aviso = ('ATENÇÃO: fontes cadastrais divergem quanto ao endereço desta unidade. '
                 'O pin é PRELIMINAR e pode estar deslocado. Confirme o endereço e a existência atual antes de se deslocar.')
    elif status == 'ponto_fora_area_referencia_pendente':
        aviso = ('ATENÇÃO: localização incompatível com a área de abrangência de referência. '
                 'O pin é PRELIMINAR e pode estar no lugar errado. Verifique endereço e funcionamento antes de ir.')
    elif status == 'suspeita_automatica_sem_referencia_externa':
        aviso = ('ATENÇÃO: nossa auditoria identificou coordenada potencialmente incorreta. '
                 'Este pin é exploratório, não é uma rota confiável. Confira endereço e existência do serviço diretamente.')
    elif origem == 'prefeitura_2024_referencia_historica':
        aviso = ('ATENÇÃO: coordenada obtida de referência municipal de 2024 compatível com o endereço cadastrado. '
                 'A localização, o endereço e a existência atual NÃO foram confirmados.')
    elif origem == 'cnes_com_correspondencia_historica_2024':
        aviso = ('ATENÇÃO: o endereço consta no CNES e é compatível com referência municipal de 2024, '
                 'mas o ponto e o funcionamento atuais NÃO foram confirmados. Confira antes de ir.')
    else:
        aviso = ('ATENÇÃO: o endereço consta no cadastro CNES, mas a localização exata e a existência atual '
                 'NÃO foram confirmadas. O pin é aproximado e pode estar incorreto; confira antes de se deslocar.')
    if ref.get('correspondencia_2024') == 'DIVERGENCIA_ENDERECO_2024':
        aviso += ' A referência municipal de 2024 apresenta endereço divergente.'
    if not verificado:
        aviso += ' O cadastro não comprova atendimento ativo, habilitação, horários ou vagas.'
    return {'coords': coords, 'pin_validado': verificado, 'origem': origem,
            'status': status, 'endereco': endereco, 'fonte': fonte,
            'fonte_url': fonte_url, 'aviso': aviso, 'observacao': observacao}


def pontos_sp(zona=None, bairro=None, categoria=None, modo='todos'):
    if zona and zona not in ZONAS:
        raise ValueError('Zona inválida')
    if categoria and categoria not in CATEGORIAS:
        raise ValueError('Categoria inválida')
    if modo not in {'todos', 'validado'}:
        raise ValueError('Modo inválido; use todos ou validado')
    if bairro and (len(bairro) > 100 or any(c in bairro for c in '<>{}')):
        raise ValueError('Bairro inválido')

    registros = [r for r in registros_consulta()
                 if r['uf'] == 'SP' and r['municipio_ibge'] == '355030'
                 and r['ambulatorial_sus_informado'] == 'SIM'
                 and (not categoria or r['categoria_indicio_nome'] == categoria)
                 and (not zona or zona_do_bairro(r['bairro']) == zona)
                 and (not bairro or normalize(r['bairro']) == normalize(bairro))]
    audited = audit_rows()
    historicos = referencias_historicas_2024()
    pontos = []
    sem_coordenada = 0
    sem_endereco = 0
    conferidos = 0
    suspeitos = 0
    for r in registros:
        if not r.get('endereco', '').strip():
            sem_endereco += 1
            continue
        detalhe = _descricao_pin(r, audited.get(r['cnes'], {}), historicos.get(r['cnes'], {}))
        coords = detalhe['coords']
        if coords is None:
            sem_coordenada += 1
            continue
        if detalhe['pin_validado']:
            conferidos += 1
        if detalhe['status'] in {'suspeita_automatica_sem_referencia_externa',
                                 'divergencia_endereco_entre_fontes',
                                 'ponto_fora_area_referencia_pendente'}:
            suspeitos += 1
        if modo == 'validado' and not detalhe['pin_validado']:
            continue
        pontos.append({
            'cnes': r['cnes'], 'nome': r['nome'], 'endereco': detalhe['endereco'],
            'bairro': r['bairro'], 'telefone': r['telefone'],
            'categoria_indicio_nome': r['categoria_indicio_nome'],
            'tipo_unidade_codigo': r.get('tipo_unidade_codigo', ''),
            'zona_preliminar': zona_do_bairro(r['bairro']),
            'latitude': round(coords[0], 7), 'longitude': round(coords[1], 7),
            'fonte_url': r['fonte_url'], 'status_verificacao': r.get('status_verificacao', 'pendente'),
            'tipo_fonte': r.get('tipo_fonte', 'indicio_nome_cnes'), 'acesso': r.get('acesso', ''),
            'status_localizacao': detalhe['status'], 'pin_validado': detalhe['pin_validado'],
            'origem_coordenada': detalhe['origem'],
            'fonte_coordenada': detalhe['fonte_url'] if detalhe['pin_validado'] else '',
            'descricao_fonte_coordenada': detalhe['fonte'],
            'observacao_localizacao': detalhe['observacao'],
            'aviso_validacao': detalhe['aviso'],
            'localizacao_conferida': detalhe['pin_validado'],
            'existencia_atual_confirmada': False,
            'endereco_atual_confirmado': detalhe['pin_validado'],
        })
    pontos.sort(key=lambda p: (p['categoria_indicio_nome'], normalize(p['nome']), p['cnes']))
    return {
        'modo': modo,
        'total_candidatos_filtro': len(registros),
        'total_com_coordenadas': len(pontos),
        'total_sem_coordenadas': sem_coordenada + sem_endereco,
        'total_sem_endereco': sem_endereco,
        'total_coordenadas_suspeitas_exibidas': suspeitos if modo == 'todos' else 0,
        'total_coordenadas_suspeitas_ocultadas': suspeitos if modo == 'validado' else 0,
        'total_pendentes_validacao_externa': len(registros) - conferidos,
        'total_pins_validados': conferidos if modo == 'todos' else len(pontos),
        'total_pins_exploratorios': len(pontos) - (conferidos if modo == 'todos' else len(pontos)),
        'total_nao_mostrados_por_modo': len(registros) - len(pontos) - sem_coordenada - sem_endereco,
        'pontos': pontos, 'situacao_base': 'mapa_completo_com_avisos_v12',
        'origem': 'CNES + Prefeitura de São Paulo AAUBS 2026 + referências municipais históricas 2024',
        'aviso': ('Mapa apresenta endereços cadastrados que tenham coordenadas utilizáveis. Somente os pins identificados '
                  'como conferidos tiveram endereço cruzado com a Prefeitura (2026). Os demais são exploratórios, '
                  'podem estar deslocados e apresentam alerta no hover/toque. Nenhuma fonte aqui garante atendimento '
                  'ativo ou disponibilidade. Registros sem coordenada seguem disponíveis na lista.'),
    }

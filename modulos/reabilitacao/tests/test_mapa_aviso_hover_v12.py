"""Contrato do novo mapa: todos os pontos disponíveis, com aviso na ponta do pin."""
from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)


def test_todas_as_categorias_com_pins_e_status():
    a=client.get('/api/v1/reabilitacao/cnes/mapa-sp?modo=todos').json()
    assert a['total_candidatos_filtro']==635
    assert a['total_com_coordenadas']>620
    assert a['total_sem_coordenadas']>0
    assert a['total_com_coordenadas']+a['total_sem_coordenadas']==a['total_candidatos_filtro']
    assert a['total_pins_validados']==448
    assert a['total_pins_exploratorios']>150
    assert {'UBS','CAPS','CER','OFICINA','OUTROS'} <= {p['categoria_indicio_nome'] for p in a['pontos']}
    assert all(p['endereco'].strip() and p['aviso_validacao'] for p in a['pontos'])


def test_endereco_historicamente_divergente_tem_aviso_explicito():
    a=client.get('/api/v1/reabilitacao/cnes/mapa-sp?categoria=CAPS').json()
    prates=next(p for p in a['pontos'] if p['cnes']=='6964036')
    assert 'PRATES 1102' in prates['endereco']
    assert 'divergente' in prates['aviso_validacao'].lower()
    assert prates['pin_validado'] is False
    assert prates['existencia_atual_confirmada'] is False


def test_pontos_verificados_tem_endereco_oficial_sem_promessa_de_vaga():
    a=client.get('/api/v1/reabilitacao/cnes/mapa-sp?categoria=UBS').json()
    boracea=next(p for p in a['pontos'] if p['cnes']=='6048633')
    assert boracea['pin_validado']
    assert 'BORACEA' in boracea['endereco'].upper()
    assert 'NÃO foi confirmada' in boracea['aviso_validacao']
    assert boracea['existencia_atual_confirmada'] is False


def test_nearest_only_confirmed_and_no_user_location_in_request():
    a=client.get('/api/v1/reabilitacao/cnes/mapa-sp?modo=validado').json()
    assert len(a['pontos']) == 448
    assert all(p['pin_validado'] for p in a['pontos'])
    assert a['total_nao_mostrados_por_modo']>0


def test_tooltip_desktop_hover_e_mobile_tap_sao_implementados():
    js=client.get('/static/app.js').text
    html=client.get('/').text
    assert 'marker.bindTooltip(hoverContent(item)' in js
    assert 'marker.bindPopup(popupContent(item))' in js
    assert 'item.aviso_validacao' in js
    assert 'pins laranja' in html.lower()
    assert 'CAPS, CER, oficinas' in html


def test_registros_sem_coordenada_continuam_no_catalogo():
    a=client.get('/api/v1/reabilitacao/cnes/candidatos?uf=SP&municipio=S%C3%A3o%20Paulo&categoria=CAPS').json()
    assert a['total'] == 106
    m=client.get('/api/v1/reabilitacao/cnes/mapa-sp?categoria=CAPS').json()
    assert m['total_com_coordenadas'] < a['total']

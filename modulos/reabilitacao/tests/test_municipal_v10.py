from fastapi.testclient import TestClient
from app.main import app
from app.geografia import pontos_sp,audit_rows

client=TestClient(app)

def test_boracea_cnes_corrigido_com_prefeitura():
    a=audit_rows()['6048633']
    assert a['status_auditoria']=='ponto_correspondente_referencia_externa'
    assert float(a['dist_cnes_referencia_km'])>20
    assert a['mostrar_pin_verificado']=='SIM'

def test_ubs_com_dado_cartografico_externo_e_bairro():
    response=client.get('/api/v1/reabilitacao/cnes/mapa-sp',params={'categoria':'UBS','modo':'validado'})
    assert response.status_code==200
    p=response.json()
    assert p['total_com_coordenadas']>=400
    assert p['total_pins_validados']==p['total_com_coordenadas']
    bor=next(x for x in p['pontos'] if x['cnes']=='6048633')
    assert bor['pin_validado'] is True
    assert 'BORACEA' in bor['endereco'].upper()

def test_servicos_nao_ubs_ainda_nao_sao_validados():
    p=client.get('/api/v1/reabilitacao/cnes/mapa-sp',params={'categoria':'CAPS','modo':'validado'}).json()
    assert p['total_pins_validados']==0

def test_conflito_endereco_nao_libera_pin():
    p=client.get('/api/v1/reabilitacao/cnes/mapa-sp',params={'categoria':'UBS','modo':'validado'}).json()
    ids={x['cnes'] for x in p['pontos']}
    assert '4049934' not in ids
    assert audit_rows()['4049934']['status_auditoria']=='divergencia_endereco_entre_fontes'

def test_summary_reporta_fontes_municipais():
    s=client.get('/api/v1/reabilitacao/cnes/auditoria-geografica/resumo').json()
    assert s['referencia_externa_registros_carregados']==485
    assert s['areas_abrangencia_2026_total']==485
    assert s['referencia_externa_matches_unicos']>=400
    assert s['pontos_fora_area']==6

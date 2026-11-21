from fastapi.testclient import TestClient
from app.main import app
from app.cnes_exploratorio import load_candidates, load_documented_offices
client=TestClient(app)

def test_documented_offices_separate_from_keyword_cnes():
    assert len(load_documented_offices())==2
    assert all(r['cnes'] not in {x['cnes'] for x in load_candidates()} for r in load_documented_offices())

def test_oficinas_sp_are_visible_without_zone():
    x=client.get('/api/v1/reabilitacao/cnes/candidatos',params={'uf':'SP','municipio':'São Paulo','categoria':'OFICINA'}).json()
    assert x['total']>=2
    ids={r['cnes'] for r in x['resultados']}
    assert {'2078015','2077655'} <= ids
    assert all(r['tipo_fonte']=='institucional_documentado' for r in x['resultados'] if r['cnes'] in ids)

def test_iot_in_oeste_and_aacd_sul():
    for zona,cnes in [('oeste','2078015'),('sul','2077655')]:
        x=client.get('/api/v1/reabilitacao/cnes/candidatos',params={'uf':'SP','municipio':'São Paulo','categoria':'OFICINA','zona':zona}).json()
        assert cnes in {r['cnes'] for r in x['resultados']}

def test_documented_bairros_in_options():
    oeste=client.get('/api/v1/reabilitacao/cnes/bairros-sp',params={'zona':'oeste','categoria':'OFICINA'}).json()
    sul=client.get('/api/v1/reabilitacao/cnes/bairros-sp',params={'zona':'sul','categoria':'OFICINA'}).json()
    assert 'CERQUEIRA CESAR' in oeste['bairros']
    assert 'VILA CLEMENTINO' in sul['bairros']

def test_documented_offices_in_list_and_exploratory_map_with_warning():
    data=client.get('/api/v1/reabilitacao/cnes/mapa-sp',params={'categoria':'OFICINA'}).json()
    assert data['total_candidatos_filtro']>=2
    assert data['total_pins_validados']==0
    assert len(data['pontos'])==2
    assert all(not r['pin_validado'] and 'ATENÇÃO' in r['aviso_validacao'] for r in data['pontos'])

"""Testa o zoneamento aproximado e os filtros por bairro e categoria na capital.

Os casos cobrem os contratos observáveis da API e dos dados de referência.
"""
from fastapi.testclient import TestClient
from app.main import app
from app.cnes_exploratorio import search_candidates, bairros_disponiveis_sp
from app.territorio_sp import zona_do_bairro

client=TestClient(app)

def test_zonas_conhecidas_e_incerta():
    assert zona_do_bairro('ITAQUERA') == 'leste'
    assert zona_do_bairro('SANTANA') == 'norte'
    assert zona_do_bairro('SANTO AMARO') == 'sul'
    assert zona_do_bairro('PINHEIROS') == 'oeste'
    assert zona_do_bairro('SE') == 'centro'
    assert zona_do_bairro('BAIRRO INVENTADO') == 'nao_identificada'

def test_zona_leste_caps():
    payload=client.get('/api/v1/reabilitacao/cnes/candidatos', params={'uf':'SP','municipio':'São Paulo','categoria':'CAPS','zona':'leste'}).json()
    assert payload['total'] > 0
    assert all(row['zona_preliminar'] == 'leste' for row in payload['resultados'])

def test_bairros_dinamicos():
    resposta=client.get('/api/v1/reabilitacao/cnes/bairros-sp', params={'zona':'leste','categoria':'CAPS'})
    assert resposta.status_code == 200
    assert 'ITAQUERA' in resposta.json()['bairros']
    assert 'SANTANA' not in resposta.json()['bairros']

def test_bairro_exato():
    payload=client.get('/api/v1/reabilitacao/cnes/candidatos',params={'uf':'SP','municipio':'São Paulo','categoria':'CAPS','bairro':'ITAQUERA'}).json()
    assert payload['total'] > 0
    assert all(row['bairro'] == 'ITAQUERA' for row in payload['resultados'])

def test_bairro_zona_contraditorios():
    payload=client.get('/api/v1/reabilitacao/cnes/candidatos',params={'uf':'SP','municipio':'São Paulo','categoria':'CAPS','bairro':'ITAQUERA','zona':'norte'}).json()
    assert payload['total'] == 0

def test_zona_fora_de_sp_bloqueada():
    resp=client.get('/api/v1/reabilitacao/cnes/candidatos',params={'uf':'RJ','municipio':'Rio de Janeiro','zona':'sul'})
    assert resp.status_code == 422

def test_paginacao_sp():
    a=client.get('/api/v1/reabilitacao/cnes/candidatos',params={'uf':'SP','municipio':'São Paulo','categoria':'CAPS','limite':8,'pagina':1}).json()
    b=client.get('/api/v1/reabilitacao/cnes/candidatos',params={'uf':'SP','municipio':'São Paulo','categoria':'CAPS','limite':8,'pagina':2}).json()
    assert a['total']==b['total']
    assert len(a['resultados'])==8 and len(b['resultados'])==8
    assert a['resultados'][0]['cnes'] != b['resultados'][0]['cnes']

def test_nao_identificada_pode_buscar():
    resp=client.get('/api/v1/reabilitacao/cnes/candidatos',params={'uf':'SP','municipio':'São Paulo','zona':'nao_identificada'}).json()
    assert all(x['zona_preliminar'] == 'nao_identificada' for x in resp['resultados'])

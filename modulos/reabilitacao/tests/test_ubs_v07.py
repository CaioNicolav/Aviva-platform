"""Testes de integração das UBS da capital, preservando serviços anteriores."""
from fastapi.testclient import TestClient
from app.main import app
from app.cnes_exploratorio import load_ubs_sp, registros_consulta

client=TestClient(app)

def test_cnes_ubs_proveniencia_e_tipo():
    ubs=load_ubs_sp()
    assert len(ubs)==487
    assert all(x['municipio_ibge']=='355030' and x['uf']=='SP' for x in ubs)
    assert all(x['ambulatorial_sus_informado']=='SIM' and x['tipo_unidade_codigo']=='2' for x in ubs)
    assert all(x['tipo_fonte']=='cnes_tipo_unidade_ubs' for x in ubs)
    assert len({r['cnes'] for r in ubs})==487

def test_nenhum_cnes_duplicado_no_catalogo():
    records=registros_consulta()
    assert len({r['cnes'] for r in records})==len(records)

def test_categoria_ubs_busca_e_filtros():
    r=client.get('/api/v1/reabilitacao/cnes/candidatos',params={'uf':'SP','municipio':'São Paulo','categoria':'UBS'})
    assert r.status_code==200
    payload=r.json()
    assert payload['total']==487
    assert all(x['categoria_indicio_nome']=='UBS' and x['tipo_fonte']=='cnes_tipo_unidade_ubs' for x in payload['resultados'])
    assert all('NÃO confirma reabilitação especializada' in x['aviso'] for x in payload['resultados'])

def test_bairros_ubs_e_filtro_especifico():
    b=client.get('/api/v1/reabilitacao/cnes/bairros-sp',params={'categoria':'UBS'}).json()
    assert b['total_bairros']>100
    bairro=b['bairros'][0]
    found=client.get('/api/v1/reabilitacao/cnes/candidatos',params={'uf':'SP','municipio':'São Paulo','categoria':'UBS','bairro':bairro}).json()
    assert found['total']>0
    assert all(x['bairro']==bairro for x in found['resultados'])

def test_map_ubs_and_nearest_input_schema():
    data=client.get('/api/v1/reabilitacao/cnes/mapa-sp',params={'categoria':'UBS','modo':'validado'}).json()
    assert data['total_candidatos_filtro']==487
    assert 0<data['total_com_coordenadas']<=487
    assert data['total_sem_coordenadas'] < 487-data['total_com_coordenadas']
    all_points=client.get('/api/v1/reabilitacao/cnes/mapa-sp?categoria=UBS&modo=todos').json()
    assert all_points['total_com_coordenadas'] + all_points['total_sem_coordenadas']==487
    assert all(x['categoria_indicio_nome']=='UBS' for x in data['pontos'])
    assert all(x['tipo_fonte']=='cnes_tipo_unidade_ubs' for x in data['pontos'])

def test_previas_oficinas_e_caps_continuam():
    oficinas=client.get('/api/v1/reabilitacao/cnes/candidatos',params={'uf':'SP','municipio':'São Paulo','categoria':'OFICINA'}).json()
    assert {'2078015','2077655'} <= {x['cnes'] for x in oficinas['resultados']}
    caps=client.get('/api/v1/reabilitacao/cnes/candidatos',params={'uf':'SP','municipio':'São Paulo','categoria':'CAPS'}).json()
    assert caps['total']>0

def test_frontend_option_and_ubs_notice():
    html=client.get('/').text
    assert '<option value="UBS">' in html
    assert 'id="ubsSearchNotice"' in html


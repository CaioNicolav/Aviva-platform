"""Mapeamento seguro de estabelecimentos candidatos. Dados de origem não equivalem a atendimento validado."""
from fastapi.testclient import TestClient
from app.main import app
from app.geografia import pontos_sp, coordenadas_sp
client = TestClient(app)


def test_mapa_geral_sp_possui_pins_com_coordenadas_reais():
    resp = client.get('/api/v1/reabilitacao/cnes/mapa-sp')
    assert resp.status_code == 200
    data = resp.json()
    assert data['total_candidatos_filtro'] > 0
    assert 0 < data['total_com_coordenadas'] <= data['total_candidatos_filtro']
    assert data['total_com_coordenadas'] + data['total_sem_coordenadas'] == data['total_candidatos_filtro']
    assert all(p['status_verificacao'] in ('pendente','oficina_documentada_atendimento_a_confirmar','ubs_cadastrada_atendimento_a_confirmar') for p in data['pontos'])
    assert all(-24.1 <= p['latitude'] <= -23.25 and -47.2 <= p['longitude'] <= -46.25 for p in data['pontos'])


def test_mapa_caps_e_bairro_correspondem_ao_filtro_da_lista():
    resp = client.get('/api/v1/reabilitacao/cnes/mapa-sp', params={'categoria':'CAPS','zona':'leste','bairro':'ITAQUERA','modo':'validado'})
    assert resp.status_code == 200
    data = resp.json()
    assert data['total_candidatos_filtro'] > 0
    assert data['total_com_coordenadas']==0  # CAPS ainda sem referência geográfica independente
    lista = client.get('/api/v1/reabilitacao/cnes/candidatos',params={'uf':'SP','municipio':'São Paulo','categoria':'CAPS','zona':'leste','bairro':'ITAQUERA'}).json()
    assert lista['total'] == data['total_candidatos_filtro']


def test_mapa_filtragem_invalida():
    assert client.get('/api/v1/reabilitacao/cnes/mapa-sp?modo=exploratorio&zona=super_norte').status_code == 422
    assert client.get('/api/v1/reabilitacao/cnes/mapa-sp?modo=exploratorio&categoria=HOSPITAL').status_code == 422


def test_coordenadas_invalidas_nao_geram_pins():
    for lat, lon in [('', '-46.6'),('NaN','-46.6'),('0','0'),('-8.1','-34.9'),('-23.5','inf')]:
        assert coordenadas_sp({'latitude': lat, 'longitude': lon}) is None


def test_endpoint_nao_solicita_geolocalizacao_do_cidadao():
    api = client.get('/openapi.json').json()['paths']['/api/v1/reabilitacao/cnes/mapa-sp']['get']
    nomes = {p['name'] for p in api['parameters']}
    assert not {'lat','lon','latitude','longitude','endereco','cep'} & nomes


def test_pontos_sao_diferentes_por_categoria():
    a = pontos_sp(categoria='CAPS')
    b = pontos_sp(categoria='CER')
    assert a['total_candidatos_filtro'] > b['total_candidatos_filtro'] > 0
    assert all(x['categoria_indicio_nome']=='CER' for x in b['pontos'])

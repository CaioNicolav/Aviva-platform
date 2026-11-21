from fastapi.testclient import TestClient
from app.main import app
from app.cnes_exploratorio import search_candidates

client = TestClient(app)


def test_resumo_cnes():
    data = client.get('/api/v1/reabilitacao/cnes/resumo').json()
    assert data['total_estabelecimentos_cnes_na_fonte'] == 642608
    assert data['total_candidatos_por_nome'] == 27779


def test_busca_capsp_sp():
    data = client.get('/api/v1/reabilitacao/cnes/candidatos?uf=SP&municipio=S%C3%A3o%20Paulo&categoria=CAPS').json()
    assert data['total'] > 0
    assert all(r['uf'] == 'SP' and r['categoria_indicio_nome'] == 'CAPS' for r in data['resultados'])
    assert all(r['status_verificacao'] == 'pendente' for r in data['resultados'])


def test_busca_cer_sp_codigo():
    data = client.get('/api/v1/reabilitacao/cnes/candidatos?uf=SP&municipio=355030&categoria=CER').json()
    assert data['total'] > 0
    assert all(r['municipio_ibge'] == '355030' for r in data['resultados'])


def test_cnes_limited():
    data = client.get('/api/v1/reabilitacao/cnes/candidatos?uf=SP&limite=5').json()
    assert 0 < len(data['resultados']) <= 5
    assert data['total'] >= len(data['resultados'])


def test_category_validation():
    assert client.get('/api/v1/reabilitacao/cnes/candidatos?categoria=DIAGNOSTICO').status_code == 422


def test_only_sus_flag_positive_by_default():
    data = search_candidates(uf='SP',categoria='CER')
    assert all(item['ambulatorial_sus_informado'] == 'SIM' for item in data['resultados'])


def test_original_validated_service_not_conflated():
    data = client.get('/api/v1/reabilitacao/servicos?uf=SP').json()
    assert data['total'] == 0
    assert data['situacao_base'] == 'sem_registros_conferidos'

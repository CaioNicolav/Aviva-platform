from fastapi.testclient import TestClient
from app.main import app
from app.service import normalize, search_services

client = TestClient(app)

def test_health():
    r = client.get('/api/v1/reabilitacao/health')
    assert r.status_code == 200 and r.json()['status'] == 'ok'

def test_modalidades():
    data = client.get('/api/v1/reabilitacao/modalidades').json()
    assert {m['id'] for m in data['modalidades']} == {'fisica','auditiva','visual','intelectual'}

def test_busca_sem_registros_nao_inventa():
    data = client.get('/api/v1/reabilitacao/servicos?uf=SP&modalidade=fisica').json()
    assert data['total'] == 0
    assert data['situacao_base'] == 'sem_registros_conferidos'

def test_uf_invalida():
    r = client.get('/api/v1/reabilitacao/servicos?uf=ZZ')
    assert r.status_code == 422

def test_normalizacao():
    assert normalize('São João') == 'sao joao'

def test_busca_registro_teste_injetado():
    fake = {'cnes': '0000000', 'nome': 'UNIDADE FICTÍCIA (APENAS TESTE)', 'uf': 'SP', 'municipio': 'São Paulo', 'modalidades': ['fisica']}
    assert len(search_services('SP','Sao Paulo','fisica', [fake])) == 1
    assert search_services('RJ','Sao Paulo','fisica', [fake]) == []

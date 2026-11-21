from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_home_tres_blocos():
    res = client.get("/")
    assert res.status_code == 200
    html = res.text
    assert 'id="buscar"' in html
    assert 'id="servicos"' in html
    assert 'id="acesso"' in html
    assert "Como começar meu atendimento?" in html
    assert "Oficina Ortopédica" in html


def test_guia_servicos():
    res = client.get('/api/v1/reabilitacao/guia-servicos')
    assert res.status_code == 200
    data=res.json()
    assert {s['id'] for s in data['servicos']} == {'ubs','cer','caps','oficina'}
    assert 'sem encaminhamento obrigatório' in data['servicos'][2]['acesso']


def test_fluxo_e_alternativas():
    res=client.get('/api/v1/reabilitacao/fluxo-acesso')
    assert res.status_code == 200
    obj=res.json()
    assert len(obj['passos'])==6
    assert {x['tipo'] for x in obj['excecoes']} == {'caps','urgencia'}


def test_versao_v05():
    res=client.get('/api/v1/reabilitacao/health')
    assert res.json()['versao']=='0.12.0'

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_frontend_sem_seletor_de_dados_nao_verificados():
    html = client.get('/').text
    js = client.get('/static/app.js').text
    assert 'id="mapMode"' not in html
    assert 'Explorar coordenadas CNES (sem validação)' not in html
    assert 'mapMode' not in js
    assert 'Sem a base municipal de referência importada' not in html

def test_mapa_completo_identifica_pins_conferidos_e_exploratorios():
    resp = client.get('/api/v1/reabilitacao/cnes/mapa-sp')
    assert resp.status_code == 200
    data = resp.json()
    assert data['modo']=='todos'
    assert data['total_pins_validados']==448
    assert data['total_com_coordenadas']==len(data['pontos'])
    assert any(p['pin_validado'] is False for p in data['pontos'])
    assert {'UBS','CAPS','CER','OFICINA','OUTROS'} <= {p['categoria_indicio_nome'] for p in data['pontos']}

def test_modo_exploratorio_bloqueado_no_backend():
    resp=client.get('/api/v1/reabilitacao/cnes/mapa-sp?modo=exploratorio')
    assert resp.status_code == 422

def test_categorias_sem_validacao_permanecem_na_lista():
    for cat in ('CAPS','CER','OFICINA'):
        mapa=client.get('/api/v1/reabilitacao/cnes/mapa-sp',params={'categoria':cat}).json()
        busca=client.get('/api/v1/reabilitacao/cnes/candidatos',params={'uf':'SP','municipio':'São Paulo','categoria':cat}).json()
        assert busca['total'] > 0
        assert mapa['total_com_coordenadas']>0
        assert mapa['total_candidatos_filtro']==busca['total']
        assert all(not p['pin_validado'] and p['aviso_validacao'] for p in mapa['pontos'])

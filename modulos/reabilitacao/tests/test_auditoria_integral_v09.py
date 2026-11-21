import csv,json
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app
from app.geografia import pontos_sp,audit_rows,audit_summary
from scripts.auditoria_integral import read_records,audit,match_references

client=TestClient(app)
ROOT=Path(__file__).resolve().parents[1]

def test_auditoria_documentou_todos_registros_da_capital():
    d=audit_rows();s=audit_summary()
    assert len(d)==s['total_avaliados']==2647
    assert len({x['cnes'] for x in d.values()})==2647
    assert s['validacao_integral_individual'] is False

def test_status_no_recorte_publico_cobre_todos():
    s=audit_summary()
    assert sum(s['status_subset_app'].values())==635
    assert s['referencia_externa_matches_unicos']==448

def test_mapa_padrao_nao_finge_posicoes_confirmadas():
    d=client.get('/api/v1/reabilitacao/cnes/mapa-sp',params={'categoria':'UBS'}).json()
    assert d['modo']=='todos'
    assert d['total_pins_validados']==448
    assert d['total_com_coordenadas']>448
    assert d['total_com_coordenadas']+d['total_sem_coordenadas']==487
    assert all('aviso_validacao' in x for x in d['pontos'])

def test_mapa_nao_permite_exploracao_nao_validada():
    r=client.get('/api/v1/reabilitacao/cnes/mapa-sp',params={'categoria':'UBS','modo':'exploratorio'})
    assert r.status_code==422
    d=client.get('/api/v1/reabilitacao/cnes/mapa-sp',params={'categoria':'UBS'}).json()
    assert d['modo']=='todos'
    assert d['total_com_coordenadas']>448
    assert any(p['pin_validado'] is False for p in d['pontos'])
    verified=client.get('/api/v1/reabilitacao/cnes/mapa-sp?categoria=UBS&modo=validado').json()
    assert all(p['pin_validado'] is True for p in verified['pontos'])

def test_enderecos_sem_pin_continuam_na_lista():
    d=client.get('/api/v1/reabilitacao/cnes/candidatos',params={'uf':'SP','municipio':'São Paulo','categoria':'UBS'}).json()
    assert d['total']==487

def test_nome_e_endereco_sem_numero_nao_fazem_match_externo():
    r=[{'cnes':'1','nome':'UBS TESTE','endereco':'RUA EXEMPLO S/N'}]
    ext=[{'nome':'UBS TESTE','endereco':'RUA EXEMPLO S/N','latitude':'-23.5','longitude':'-46.6'}]
    assert match_references(r,ext)=={}

def test_mesmo_cnes_permite_match_unico_se_ha_coordenada_externa():
    r=[{'cnes':'123','nome':'UBS TESTE','endereco':'RUA A 10'}]
    ext=[{'cnes':'123','latitude':'-23.5','longitude':'-46.6'}]
    d=match_references(r,ext)
    assert d['123']['metodo']=='identificador_cnes'
    assert d['123']['coordenada_referencia']==(-23.5,-46.6)

def test_geojson_ref_sem_cnes_nao_gera_falso_match():
    r=[{'cnes':'12','nome':'UBS ALFA','endereco':'RUA QUATRO 10'}]
    ext=[{'nome':'UBS ALFA','endereco':'RUA QUATRO 11','latitude':'-23.5','longitude':'-46.6'}]
    assert match_references(r,ext)=={}

def test_api_resumo_mostra_limitacoes():
    d=client.get('/api/v1/reabilitacao/cnes/auditoria-geografica/resumo').json()
    assert d['total_avaliados']==2647 and d['validacao_integral_individual'] is False

def test_modo_desconhecido_rejeitado():
    assert client.get('/api/v1/reabilitacao/cnes/mapa-sp?modo=falso').status_code==422

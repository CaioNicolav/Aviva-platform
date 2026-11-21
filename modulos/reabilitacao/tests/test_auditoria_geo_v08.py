from app.auditoria_geo import auditoria_sp, distancia_km
from app.geografia import pontos_sp
from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)

def test_ubs_boracea_validada_por_fonte_municipal_em_v10():
    # O ponto antes suspeito recebeu coordenada oficial da Prefeitura.
    from app.geografia import audit_rows
    a=audit_rows()['6048633']
    assert a['status_auditoria']=='ponto_correspondente_referencia_externa'
    assert a['mostrar_pin_verificado']=='SIM'
    assert float(a['dist_cnes_referencia_km'])>20
    assert any(p['cnes']=='6048633' for p in pontos_sp(categoria='UBS')['pontos'])

def test_pontos_sem_confirmacao_externa_nao_entram_na_proximidade():
    from app.geografia import audit_rows
    audit=audit_rows()
    result=client.get('/api/v1/reabilitacao/cnes/mapa-sp?categoria=UBS&modo=validado').json()
    assert result['total_coordenadas_suspeitas_ocultadas']>0
    assert all(audit[p['cnes']]['status_auditoria']=='ponto_correspondente_referencia_externa' for p in result['pontos'])
    assert result['total_com_coordenadas']==result['total_pins_validados']==448
    assert result['total_nao_mostrados_por_modo'] > 0

def test_caps_boracea_e_ubs_boracea_unidades_distintas():
    from app.cnes_exploratorio import registros_consulta
    r={x['cnes']:x for x in registros_consulta()}
    assert '6048633' in r and '2960303' in r
    assert r['6048633']['categoria_indicio_nome']=='UBS'
    assert r['2960303']['categoria_indicio_nome']=='CAPS'

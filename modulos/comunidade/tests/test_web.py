"""Verifica o servidor HTTP local e os endpoints do painel Comunidade.

Inclui respostas da API, dados territoriais e comportamento de consultas externas."""

import csv
import json
import threading
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit
from urllib.request import Request, urlopen

import pytest

from aviva.web import (
    ServidorAviva,
    _consultar_equipamentos,
    _consultar_bairros,
    _ponto_na_geometria,
    carregar_bairros_distrito,
    carregar_distritos,
    carregar_serie_climatica,
    carregar_servicos_distrito,
)


def _criar_base(caminho):
    with caminho.open("w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(
            arquivo,
            fieldnames=("data", "estacao", "horas_com_chuva", "chuva_dia_mm"),
        )
        escritor.writeheader()
        escritor.writerows(
            [
                {
                    "data": "2026-01-01",
                    "estacao": "A701",
                    "horas_com_chuva": 2,
                    "chuva_dia_mm": 4.5,
                },
                {
                    "data": "2026-01-02",
                    "estacao": "A701",
                    "horas_com_chuva": 0,
                    "chuva_dia_mm": 0,
                },
                {
                    "data": "2026-01-01",
                    "estacao": "A771",
                    "horas_com_chuva": 1,
                    "chuva_dia_mm": 2.0,
                },
            ]
        )


def _iniciar_servidor(caminho_dados):
    servidor = ServidorAviva(("127.0.0.1", 0), caminho_dados=caminho_dados)
    thread = threading.Thread(target=servidor.serve_forever, daemon=True)
    thread.start()
    return servidor, thread, "http://127.0.0.1:%s" % servidor.server_port


def test_carregar_serie_entrega_observacoes_por_estacao(tmp_path):
    caminho = tmp_path / "base.csv"
    _criar_base(caminho)

    resultado = carregar_serie_climatica(caminho, dias=1)

    assert resultado["total_observacoes"] == 3
    assert resultado["ultima_observacao"] == "2026-01-02"
    assert [estacao["codigo"] for estacao in resultado["estacoes"]] == [
        "A701",
        "A771",
    ]
    assert resultado["estacoes"][0]["serie"] == [
        {
            "data": "2026-01-02",
            "chuva_dia_mm": 0.0,
            "horas_com_chuva": 0,
        }
    ]


def test_carregar_serie_rejeita_periodo_invalido(tmp_path):
    caminho = tmp_path / "base.csv"
    _criar_base(caminho)

    with pytest.raises(ValueError, match="entre 1 e 30 dias"):
        carregar_serie_climatica(caminho, dias=31)


def test_carregar_serie_nao_inventa_colunas_ausentes(tmp_path):
    caminho = tmp_path / "base.csv"
    caminho.write_text("data,estacao\n2026-01-01,A701\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Colunas ausentes"):
        carregar_serie_climatica(caminho)


def test_carregar_serie_rejeita_dia_e_estacao_duplicados(tmp_path):
    caminho = tmp_path / "base.csv"
    _criar_base(caminho)
    with caminho.open("a", newline="", encoding="utf-8") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(("2026-01-01", "A701", 3, 5.0))

    with pytest.raises(ValueError, match="Observação duplicada"):
        carregar_serie_climatica(caminho)


def test_carregar_distritos_entrega_os_96_distritos_oficiais():
    resultado = carregar_distritos()

    assert len(resultado["distritos"]) == 96
    assert resultado["fonte"].startswith("IBGE")
    assert len({item["codigo_ibge"] for item in resultado["distritos"]}) == 96
    assert "Vila Mariana" in {item["nome"] for item in resultado["distritos"]}
    assert "\u00c1gua Rasa" in {item["nome"] for item in resultado["distritos"]}


def test_carregar_distritos_rejeita_base_incompleta(tmp_path):
    caminho = tmp_path / "distritos.json"
    caminho.write_text(
        json.dumps({"distritos": [{"codigo_ibge": 355030801, "nome": "Água Rasa"}]}),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="96 distritos"):
        carregar_distritos(caminho)


def test_ponto_na_geometria_respeita_limite_e_buracos():
    geometria = {
        "type": "Polygon",
        "coordinates": [
            [
                [-47, -24],
                [-46, -24],
                [-46, -23],
                [-47, -23],
                [-47, -24],
            ],
            [
                [-46.7, -23.7],
                [-46.3, -23.7],
                [-46.3, -23.3],
                [-46.7, -23.3],
                [-46.7, -23.7],
            ],
        ],
    }

    assert _ponto_na_geometria(-46.9, -23.9, geometria)
    assert not _ponto_na_geometria(-46.5, -23.5, geometria)
    assert not _ponto_na_geometria(-45.9, -23.5, geometria)


def test_consulta_osm_de_servicos_nao_carrega_bairros(monkeypatch):
    consulta_recebida = {}

    def consultar(url, timeout):
        consulta_recebida["url"] = url
        consulta_recebida["timeout"] = timeout
        return {"elements": []}

    monkeypatch.setattr("aviva.web._consultar_json", consultar)

    assert _consultar_equipamentos(
        {"sul": -23.7, "oeste": -46.7, "norte": -23.5, "leste": -46.6}
    ) == []

    parametros = parse_qs(urlsplit(consulta_recebida["url"]).query)
    consulta = parametros["data"][0]
    assert 'nwr["place"' not in consulta
    assert "out center tags" in consulta
    assert consulta_recebida["timeout"] == 45


def test_consulta_osm_de_bairros_busca_apenas_localidades(monkeypatch):
    consulta_recebida = {}

    def consultar(url, timeout):
        consulta_recebida["url"] = url
        consulta_recebida["timeout"] = timeout
        return {"elements": []}

    monkeypatch.setattr("aviva.web._consultar_json", consultar)

    assert _consultar_bairros(
        {"sul": -23.7, "oeste": -46.7, "norte": -23.5, "leste": -46.6}
    ) == []

    consulta = parse_qs(urlsplit(consulta_recebida["url"]).query)["data"][0]
    assert 'nwr["place"~"^(suburb|neighbourhood|quarter)$"]' in consulta
    assert "amenity" not in consulta
    assert consulta_recebida["timeout"] == 35


def test_carregar_servicos_filtra_pelo_limite_e_classifica_por_categoria(
    monkeypatch,
):
    distrito = next(
        item
        for item in carregar_distritos()["distritos"]
        if item["nome"] == "Vila Mariana"
    )
    geometria = {
        "type": "Polygon",
        "coordinates": [[
            [-46.7, -23.7],
            [-46.6, -23.7],
            [-46.6, -23.5],
            [-46.7, -23.5],
            [-46.7, -23.7],
        ]],
    }
    monkeypatch.setattr("aviva.web._cache_servicos", {})
    monkeypatch.setattr(
        "aviva.web._geocodificar_distrito",
        lambda nome: {
            "geometria": geometria,
            "latitude": -23.6,
            "longitude": -46.65,
            "bbox": {
                "sul": -23.7,
                "norte": -23.5,
                "oeste": -46.7,
                "leste": -46.6,
            },
        },
    )
    monkeypatch.setattr(
        "aviva.web._consultar_equipamentos",
        lambda bbox: [
            {
                "type": "node",
                "id": 1,
                "lat": -23.58,
                "lon": -46.63,
                "tags": {
                    "amenity": "hospital",
                    "name": "Hospital de teste",
                    "operator:type": "public",
                    "addr:street": "Rua Central",
                    "addr:housenumber": "10",
                    "addr:neighbourhood": "Vila Mariana",
                },
            },
            {
                "type": "node",
                "id": 2,
                "lat": -23.58,
                "lon": -46.64,
                "tags": {
                    "amenity": "police",
                    "name": "Delegacia de teste",
                    "operator": "Polícia Civil do Estado de São Paulo",
                },
            },
            {
                "type": "node",
                "id": 3,
                "lat": -23.58,
                "lon": -46.55,
                "tags": {"amenity": "school", "name": "Escola fora do distrito"},
            },
            {
                "type": "node",
                "id": 4,
                "lat": -23.59,
                "lon": -46.62,
                "tags": {
                    "amenity": "school",
                    "name": "Escola privada de teste",
                    "operator": "Instituição particular",
                },
            },
        ],
    )

    resultado = carregar_servicos_distrito(distrito["codigo_ibge"])

    assert resultado["distrito"] == "Vila Mariana"
    assert resultado["total"] == 3
    assert resultado["contagem_por_categoria"]["saude"] == 1
    assert resultado["contagem_publicos"] == 2
    hospital = next(ponto for ponto in resultado["pontos"] if ponto["nome"] == "Hospital de teste")
    escola = next(ponto for ponto in resultado["pontos"] if ponto["nome"] == "Escola privada de teste")
    assert hospital["gestao_publica_indicada"] is True
    assert hospital["endereco"] == "Rua Central 10"
    assert escola["gestao_publica_indicada"] is False


def test_carregar_bairros_busca_localidades_e_filtra_limite(monkeypatch):
    distrito = next(
        item
        for item in carregar_distritos()["distritos"]
        if item["nome"] == "Vila Mariana"
    )
    geometria = {
        "type": "Polygon",
        "coordinates": [[
            [-46.7, -23.7],
            [-46.6, -23.7],
            [-46.6, -23.5],
            [-46.7, -23.5],
            [-46.7, -23.7],
        ]],
    }
    monkeypatch.setattr("aviva.web._cache_bairros", {})
    monkeypatch.setattr(
        "aviva.web._geocodificar_distrito",
        lambda nome: {
            "geometria": geometria,
            "latitude": -23.6,
            "longitude": -46.65,
            "bbox": {
                "sul": -23.7,
                "norte": -23.5,
                "oeste": -46.7,
                "leste": -46.6,
            },
        },
    )
    monkeypatch.setattr(
        "aviva.web._consultar_bairros",
        lambda bbox: [
            {
                "type": "node",
                "id": 1,
                "lat": -23.58,
                "lon": -46.63,
                "tags": {"place": "neighbourhood", "name": "Aclimação"},
            },
            {
                "type": "way",
                "id": 2,
                "center": {"lat": -23.59, "lon": -46.64},
                "tags": {"place": "quarter", "name": "Vila Mariana"},
            },
            {
                "type": "node",
                "id": 3,
                "lat": -23.58,
                "lon": -46.55,
                "tags": {"place": "neighbourhood", "name": "Fora do distrito"},
            },
        ],
    )

    resultado = carregar_bairros_distrito(distrito["codigo_ibge"])

    assert resultado["distrito"] == "Vila Mariana"
    assert resultado["bairros"] == ["Aclimação", "Vila Mariana"]
    assert resultado["fonte"].startswith("OpenStreetMap")


def test_api_serves_climate_and_python_classification(tmp_path):
    caminho = tmp_path / "base.csv"
    _criar_base(caminho)
    servidor, thread, base_url = _iniciar_servidor(caminho)

    try:
        with urlopen(base_url + "/api/clima?dias=2") as resposta:
            clima = json.loads(resposta.read().decode("utf-8"))
            assert resposta.status == 200
            assert resposta.headers["Content-Security-Policy"]
            assert clima["total_observacoes"] == 3

        with urlopen(base_url + "/api/distritos") as resposta:
            distritos = json.loads(resposta.read().decode("utf-8"))
            assert resposta.status == 200
            assert resposta.headers["Content-Security-Policy"]
            assert len(distritos["distritos"]) == 96
            assert "frame-src https://www.openstreetmap.org" in resposta.headers[
                "Content-Security-Policy"
            ]

        requisicao = Request(
            base_url + "/api/avaliar",
            data=json.dumps(
                {"nivel_agua_cm": 130, "chuva_mm_h": 10}
            ).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(requisicao) as resposta:
            avaliacao = json.loads(resposta.read().decode("utf-8"))
            assert resposta.status == 200
            assert avaliacao["nivel"] == "ATENÇÃO"
            assert avaliacao["aviso"]

        requisicao_invalida = Request(
            base_url + "/api/avaliar",
            data=json.dumps(
                {"nivel_agua_cm": -1, "chuva_mm_h": 10}
            ).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with pytest.raises(HTTPError) as erro:
            urlopen(requisicao_invalida)
        assert erro.value.code == 400
        payload = json.loads(erro.value.read().decode("utf-8"))
        assert payload["ok"] is False
        assert payload["erros"]

        with urlopen(base_url + "/") as resposta:
            pagina = resposta.read().decode("utf-8")
            assert resposta.status == 200
            assert "A cidade fica" in pagina
            assert "Dados comunitários do OpenStreetMap" in pagina
            assert 'id="city-select"' in pagina
            assert 'id="neighborhood-options"' in pagina
            assert "Criar um encontro" in pagina
            assert 'id="community-storage-status"' in pagina
    finally:
        servidor.shutdown()
        servidor.server_close()
        thread.join(timeout=2)


def test_api_serves_osm_places_for_selected_official_district(
    tmp_path, monkeypatch
):
    caminho = tmp_path / "base.csv"
    _criar_base(caminho)
    distrito = next(
        item
        for item in carregar_distritos()["distritos"]
        if item["nome"] == "Vila Mariana"
    )
    monkeypatch.setattr(
        "aviva.web.carregar_servicos_distrito",
        lambda codigo: {
            "codigo_ibge": codigo,
            "distrito": "Vila Mariana",
            "fonte": "OpenStreetMap",
            "pontos": [],
            "total": 0,
            "bairros": [],
            "contagem_publicos": 0,
            "categorias": {},
            "contagem_por_categoria": {},
        },
    )
    monkeypatch.setattr(
        "aviva.web.carregar_bairros_distrito",
        lambda codigo: {
            "codigo_ibge": codigo,
            "distrito": "Vila Mariana",
            "bairros": ["Aclimação"],
            "fonte": "OpenStreetMap",
        },
    )
    servidor, thread, base_url = _iniciar_servidor(caminho)

    try:
        with urlopen(
            base_url + f"/api/servicos?distrito={distrito['codigo_ibge']}"
        ) as resposta:
            dados = json.loads(resposta.read().decode("utf-8"))
            assert resposta.status == 200
            assert dados["distrito"] == "Vila Mariana"
            assert dados["fonte"] == "OpenStreetMap"

        with urlopen(
            base_url + f"/api/bairros?distrito={distrito['codigo_ibge']}"
        ) as resposta:
            dados = json.loads(resposta.read().decode("utf-8"))
            assert resposta.status == 200
            assert dados["distrito"] == "Vila Mariana"
            assert dados["bairros"] == ["Aclimação"]

        with pytest.raises(HTTPError) as erro:
            urlopen(base_url + "/api/servicos?distrito=0")
        assert erro.value.code == 404

        with pytest.raises(HTTPError) as erro:
            urlopen(base_url + "/api/bairros?distrito=0")
        assert erro.value.code == 404
    finally:
        servidor.shutdown()
        servidor.server_close()
        thread.join(timeout=2)

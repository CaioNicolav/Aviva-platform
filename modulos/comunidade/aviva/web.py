"""Atende as rotas HTTP locais do painel Comunidade e seus arquivos estáticos.

Lê séries climáticas e distritos dos arquivos locais, disponibiliza dados
para o front-end e consulta OpenStreetMap para serviços e localidades.
As consultas externas são exploratórias e não comprovam atendimento."""

import argparse
import csv
import json
import math
import threading
import time
import unicodedata
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlsplit
from urllib.request import Request, urlopen

from aviva.config import AVISO
from aviva.monitor import MonitorRisco


ROOT_DIR = Path(__file__).resolve().parents[1]
WEB_DIR = ROOT_DIR / "web"
BASE_CLIMA = ROOT_DIR / "entregas" / "pensamento-computacional" / "base_estatistica.csv"
BASE_DISTRITOS = ROOT_DIR / "data" / "distritos_sao_paulo.json"
COLUNAS_CLIMA = ("data", "estacao", "horas_com_chuva", "chuva_dia_mm")
ARQUIVOS_ESTATICOS = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/index.html": ("index.html", "text/html; charset=utf-8"),
    "/styles.css": ("styles.css", "text/css; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
    "/aviva-marca.svg": ("aviva-marca.svg", "image/svg+xml"),
}
TAMANHO_MAXIMO_REQUISICAO = 8192
USER_AGENT_OPENSTREETMAP = (
    "AVIVA-CitizenTech/1.0 "
    "(https://github.com/leonardoferreiraads/Aviva)"
)
TEMPO_CACHE_SERVICOS = 1800
_cache_servicos = {}
_cache_bairros = {}
_cache_geocodificacao = {}
_lock_cache_servicos = threading.Lock()
_lock_cache_bairros = threading.Lock()
_lock_geocodificacao = threading.Lock()
_lock_overpass = threading.Lock()
_ultima_consulta_geocodificacao = 0.0
_categorias_servicos = {
    "saude": "Saúde",
    "educacao": "Educação",
    "assistencia": "Assistência social",
    "seguranca": "Segurança e proteção",
    "cultura": "Cultura e convivência",
    "governo": "Administração pública",
}


def carregar_serie_climatica(caminho=BASE_CLIMA, dias=14):
    """Lê observações completas do CSV local e prepara as séries do painel."""
    caminho = Path(caminho)
    if not caminho.is_file():
        raise FileNotFoundError(f"Arquivo de dados climáticos não encontrado: {caminho}")
    if not 1 <= dias <= 30:
        raise ValueError("O período solicitado deve estar entre 1 e 30 dias.")

    por_estacao = {}
    chaves_registradas = set()
    with caminho.open("r", newline="", encoding="utf-8-sig") as arquivo:
        leitor = csv.DictReader(arquivo)
        ausentes = set(COLUNAS_CLIMA) - set(leitor.fieldnames or ())
        if ausentes:
            raise ValueError(
                "Colunas ausentes na base climática: " + ", ".join(sorted(ausentes))
            )
        for numero_linha, linha in enumerate(leitor, start=2):
            try:
                data = date.fromisoformat(linha["data"])
                horas = int(linha["horas_com_chuva"])
                chuva = float(linha["chuva_dia_mm"])
            except (TypeError, ValueError) as erro:
                raise ValueError(
                    f"Registro inválido na linha {numero_linha} da base climática."
                ) from erro
            estacao = linha["estacao"].strip()
            if not estacao:
                raise ValueError(
                    f"Identificador da estação ausente na linha {numero_linha}."
                )
            if horas < 0 or horas > 24 or chuva < 0:
                raise ValueError(
                    f"Valores fora da faixa esperada na linha {numero_linha}."
                )
            if not math.isfinite(chuva):
                raise ValueError(
                    f"Precipitação inválida na linha {numero_linha} da base climática."
                )
            chave = (estacao, data)
            if chave in chaves_registradas:
                raise ValueError(
                    f"Observação duplicada da estação {estacao} em {data.isoformat()}."
                )
            chaves_registradas.add(chave)
            por_estacao.setdefault(estacao, []).append(
                {
                    "data": data.isoformat(),
                    "chuva_dia_mm": round(chuva, 1),
                    "horas_com_chuva": horas,
                }
            )

    if not por_estacao:
        raise ValueError("A base climática não contém observações.")

    nomes_estacoes = {
        "A701": "São Paulo — Mirante",
        "A771": "São Paulo — Interlagos",
    }
    estacoes = []
    for codigo, registros in sorted(por_estacao.items()):
        registros.sort(key=lambda registro: registro["data"])
        observacoes = registros[-dias:]
        ultima = registros[-1]
        estacoes.append(
            {
                "codigo": codigo,
                "nome": nomes_estacoes.get(codigo, codigo),
                "total_observacoes": len(registros),
                "ultima_data": ultima["data"],
                "ultima_chuva_mm": ultima["chuva_dia_mm"],
                "ultima_horas_com_chuva": ultima["horas_com_chuva"],
                "serie": observacoes,
            }
        )

    todas_datas = [estacao["ultima_data"] for estacao in estacoes]
    return {
        "fonte": "INMET — observações históricas das estações meteorológicas",
        "periodo_inicio": min(
            registro["data"]
            for estacao in por_estacao.values()
            for registro in estacao
        ),
        "ultima_observacao": max(todas_datas),
        "total_observacoes": sum(
            estacao["total_observacoes"] for estacao in estacoes
        ),
        "estacoes": estacoes,
    }


def carregar_distritos(caminho=BASE_DISTRITOS):
    """Lê a lista oficial de distritos do município de São Paulo."""
    caminho = Path(caminho)
    if not caminho.is_file():
        raise FileNotFoundError(f"Arquivo de distritos não encontrado: {caminho}")
    with caminho.open("r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)

    distritos = dados.get("distritos") if isinstance(dados, dict) else None
    if not isinstance(distritos, list) or len(distritos) != 96:
        raise ValueError("A base deve conter os 96 distritos oficiais de São Paulo.")
    codigos = set()
    for distrito in distritos:
        if not isinstance(distrito, dict):
            raise ValueError("Registro inválido na base de distritos.")
        codigo = distrito.get("codigo_ibge")
        nome = distrito.get("nome")
        if (
            not isinstance(codigo, int)
            or not str(codigo).startswith("3550308")
            or not isinstance(nome, str)
            or not nome.strip()
            or codigo in codigos
        ):
            raise ValueError("Registro inválido ou duplicado na base de distritos.")
        codigos.add(codigo)
    return dados


def _consultar_json(url, timeout):
    requisicao = Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": USER_AGENT_OPENSTREETMAP,
        },
    )
    with urlopen(requisicao, timeout=timeout) as resposta:
        return json.loads(resposta.read().decode("utf-8"))


def _geocodificar_distrito(nome):
    """Obtém o limite administrativo do distrito no Nominatim."""
    global _ultima_consulta_geocodificacao
    with _lock_geocodificacao:
        intervalo = time.monotonic() - _ultima_consulta_geocodificacao
        if intervalo < 1:
            time.sleep(1 - intervalo)
        parametros = urlencode(
            {
                "q": f"{nome}, São Paulo, SP, Brasil",
                "format": "jsonv2",
                "addressdetails": 1,
                "polygon_geojson": 1,
                "limit": 1,
            }
        )
        try:
            if nome in _cache_geocodificacao:
                resultados = _cache_geocodificacao[nome]
            else:
                resultados = _consultar_json(
                    f"https://nominatim.openstreetmap.org/search?{parametros}",
                    timeout=20,
                )
                if resultados:
                    _cache_geocodificacao[nome] = resultados
        finally:
            _ultima_consulta_geocodificacao = time.monotonic()
    if not resultados:
        raise ValueError(f"O OpenStreetMap não localizou o distrito {nome}.")
    distrito = resultados[0]
    geometria = distrito.get("geojson")
    if (
        distrito.get("type") != "administrative"
        or distrito.get("osm_type") != "relation"
        or not isinstance(geometria, dict)
        or geometria.get("type") not in {"Polygon", "MultiPolygon"}
    ):
        raise ValueError(
            f"Não há limite administrativo confiável mapeado para {nome}."
        )
    try:
        latitude = float(distrito["lat"])
        longitude = float(distrito["lon"])
        sul, norte, oeste, leste = map(float, distrito["boundingbox"])
    except (KeyError, TypeError, ValueError) as erro:
        raise ValueError(
            f"O limite geográfico de {nome} está incompleto na fonte."
        ) from erro
    if (
        not all(
            math.isfinite(valor)
            for valor in (latitude, longitude, sul, norte, oeste, leste)
        )
        or not -90 <= latitude <= 90
        or not -180 <= longitude <= 180
        or sul >= norte
        or oeste >= leste
    ):
        raise ValueError(f"O limite geográfico de {nome} é inválido.")
    return {
        "geometria": geometria,
        "latitude": latitude,
        "longitude": longitude,
        "bbox": {"sul": sul, "norte": norte, "oeste": oeste, "leste": leste},
    }


def _ponto_no_anel(longitude, latitude, anel):
    dentro = False
    anterior = len(anel) - 1
    for indice, coordenada in enumerate(anel):
        x_atual, y_atual = coordenada[:2]
        x_anterior, y_anterior = anel[anterior][:2]
        cruza = (y_atual > latitude) != (y_anterior > latitude)
        if cruza:
            x_intersecao = (
                (x_anterior - x_atual)
                * (latitude - y_atual)
                / (y_anterior - y_atual)
                + x_atual
            )
            if longitude < x_intersecao:
                dentro = not dentro
        anterior = indice
    return dentro


def _ponto_na_geometria(longitude, latitude, geometria):
    """Verifica se um ponto OSM está dentro do limite distrital GeoJSON."""
    tipo = geometria["type"]
    coordenadas = geometria["coordinates"]
    poligonos = [coordenadas] if tipo == "Polygon" else coordenadas
    for poligono in poligonos:
        if not poligono or not _ponto_no_anel(longitude, latitude, poligono[0]):
            continue
        if not any(
            _ponto_no_anel(longitude, latitude, furo)
            for furo in poligono[1:]
        ):
            return True
    return False


def _consultar_equipamentos(bbox):
    """Busca serviços locais no Overpass, limitando a consulta ao distrito."""
    sul = bbox["sul"]
    oeste = bbox["oeste"]
    norte = bbox["norte"]
    leste = bbox["leste"]
    filtros = (
        'nwr["amenity"~"hospital|clinic|doctors|school|kindergarten|college|university|social_facility|social_centre|library|community_centre|police|fire_station|townhall|public_building|courthouse"]'
        f"({sul},{oeste},{norte},{leste});"
        'nwr["healthcare"~"hospital|clinic|doctor|centre"]'
        f"({sul},{oeste},{norte},{leste});"
        'nwr["office"~"government|public_administration"]'
        f"({sul},{oeste},{norte},{leste});"
    )
    consulta = f"[out:json][timeout:35];({filtros});out center tags;"
    parametros = urlencode({"data": consulta})
    url = f"https://overpass-api.de/api/interpreter?{parametros}"
    with _lock_overpass:
        resultado = _consultar_json(url, timeout=45)
    if not isinstance(resultado, dict) or not isinstance(
        resultado.get("elements"), list
    ):
        raise ValueError("A fonte cartográfica retornou uma resposta inválida.")
    return resultado["elements"]


def _classificar_equipamento(tags):
    amenity = tags.get("amenity", "")
    healthcare = tags.get("healthcare", "")
    office = tags.get("office", "")
    if amenity in {"hospital", "clinic", "doctors"} or healthcare in {
        "hospital",
        "clinic",
        "doctor",
        "centre",
    }:
        return "saude", "Unidade de saúde"
    if amenity in {"school", "kindergarten", "college", "university"}:
        return "educacao", "Unidade de ensino"
    if amenity in {"social_facility", "social_centre"}:
        return "assistencia", "Serviço de assistência social"
    if amenity in {"police", "fire_station"}:
        return "seguranca", (
            "Polícia" if amenity == "police" else "Corpo de Bombeiros"
        )
    if amenity in {"library", "community_centre"}:
        return "cultura", (
            "Biblioteca" if amenity == "library" else "Centro comunitário"
        )
    if amenity in {"townhall", "public_building", "courthouse"} or office in {
        "government",
        "public_administration",
    }:
        return "governo", "Órgão ou serviço público"
    return None


def _consultar_bairros(bbox):
    """Busca somente localidades nomeadas no Overpass, sem carregar serviços."""
    consulta = (
        "[out:json][timeout:25];("
        'nwr["place"~"^(suburb|neighbourhood|quarter)$"]'
        f"({bbox['sul']},{bbox['oeste']},{bbox['norte']},{bbox['leste']});"
        ");out center tags;"
    )
    parametros = urlencode({"data": consulta})
    resultado = _consultar_json(
        f"https://overpass-api.de/api/interpreter?{parametros}",
        timeout=35,
    )
    if not isinstance(resultado, dict) or not isinstance(
        resultado.get("elements"), list
    ):
        raise ValueError("A fonte cartográfica retornou uma lista de bairros inválida.")
    return resultado["elements"]


def _gestao_publica_indicada(tags):
    operador = unicodedata.normalize(
        "NFKD", tags.get("operator", "")
    ).encode("ascii", "ignore").decode("ascii").casefold()
    termos_publicos = (
        "policia militar",
        "policia civil",
        "governo do estado",
        "secretaria municipal",
        "secretaria estadual",
        "prefeitura",
        "ministerio publico",
        "instituto nacional do seguro social",
        "inss",
    )
    return (
        tags.get("operator:type", "").casefold() in {"public", "government"}
        or tags.get("amenity")
        in {"police", "fire_station", "townhall", "public_building", "courthouse"}
        or any(termo in operador for termo in termos_publicos)
    )


def _distancia_em_km(lat1, lon1, lat2, lon2):
    raio_terra = 6371
    lat1, lon1, lat2, lon2 = map(
        math.radians, (lat1, lon1, lat2, lon2)
    )
    diferenca_lat = lat2 - lat1
    diferenca_lon = lon2 - lon1
    a = (
        math.sin(diferenca_lat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(diferenca_lon / 2) ** 2
    )
    return 2 * raio_terra * math.asin(math.sqrt(a))


def carregar_servicos_distrito(codigo_distrito):
    """Retorna equipamentos e localidades OSM no distrito selecionado."""
    distritos = carregar_distritos()["distritos"]
    distrito = next(
        (item for item in distritos if item["codigo_ibge"] == codigo_distrito),
        None,
    )
    if distrito is None:
        raise ValueError("Selecione um distrito oficial de São Paulo.")

    agora = time.monotonic()
    with _lock_cache_servicos:
        registro = _cache_servicos.get(codigo_distrito)
        if registro is not None and agora - registro[0] < TEMPO_CACHE_SERVICOS:
            return registro[1]

    limite = _geocodificar_distrito(distrito["nome"])
    elementos = _consultar_equipamentos(limite["bbox"])
    pontos = []
    identificadores = set()
    for elemento in elementos:
        identificador = (elemento.get("type"), elemento.get("id"))
        if identificador in identificadores:
            continue
        identificadores.add(identificador)
        tags = elemento.get("tags", {})
        classificacao = _classificar_equipamento(tags)
        if classificacao is None:
            continue
        coordenadas = elemento.get("center", elemento)
        try:
            latitude = float(coordenadas["lat"])
            longitude = float(coordenadas["lon"])
        except (KeyError, TypeError, ValueError):
            continue
        if not _ponto_na_geometria(
            longitude, latitude, limite["geometria"]
        ):
            continue
        nome = tags.get("name") or tags.get("name:pt") or tags.get("short_name")
        if not nome:
            continue
        categoria, tipo = classificacao
        rua = tags.get("addr:street")
        numero = tags.get("addr:housenumber")
        endereco = tags.get("addr:full")
        if not endereco and rua:
            endereco = " ".join(parte for parte in (rua, numero) if parte)
        operador = tags.get("operator")
        pontos.append(
            {
                "nome": str(nome)[:160],
                "categoria": categoria,
                "tipo": tipo,
                "endereco": str(endereco)[:180] if endereco else "",
                "operador": str(operador)[:100] if operador else "",
                "gestao_publica_indicada": _gestao_publica_indicada(tags),
                "distancia_centro_km": round(
                    _distancia_em_km(
                        limite["latitude"],
                        limite["longitude"],
                        latitude,
                        longitude,
                    ),
                    1,
                ),
                "latitude": latitude,
                "longitude": longitude,
                "osm_url": (
                    "https://www.openstreetmap.org/"
                    f"{elemento['type']}/{elemento['id']}"
                ),
            }
        )

    pontos.sort(
        key=lambda ponto: (
            ponto["categoria"],
            ponto["distancia_centro_km"],
            ponto["nome"].casefold(),
        )
    )
    contagem_por_categoria = {
        chave: sum(ponto["categoria"] == chave for ponto in pontos)
        for chave in _categorias_servicos
    }
    contagem_publicos = sum(
        ponto["gestao_publica_indicada"] for ponto in pontos
    )
    resultado = {
        "distrito": distrito["nome"],
        "codigo_ibge": codigo_distrito,
        "centro": {
            "latitude": limite["latitude"],
            "longitude": limite["longitude"],
        },
        "bbox": limite["bbox"],
        "categorias": _categorias_servicos,
        "total": len(pontos),
        "contagem_publicos": contagem_publicos,
        "contagem_por_categoria": contagem_por_categoria,
        "pontos": pontos[:150],
        "fonte": (
            "OpenStreetMap contributors — Nominatim e Overpass API"
        ),
        "licenca": "Open Database License (ODbL)",
        "consultado_em": date.today().isoformat(),
    }
    with _lock_cache_servicos:
        _cache_servicos[codigo_distrito] = (time.monotonic(), resultado)
    return resultado


def carregar_bairros_distrito(codigo_distrito):
    """Retorna localidades nomeadas do OSM sem depender da consulta de serviços."""
    distritos = carregar_distritos()["distritos"]
    distrito = next(
        (item for item in distritos if item["codigo_ibge"] == codigo_distrito),
        None,
    )
    if distrito is None:
        raise ValueError("Selecione um distrito oficial de São Paulo.")

    agora = time.monotonic()
    with _lock_cache_bairros:
        registro = _cache_bairros.get(codigo_distrito)
        if registro is not None and agora - registro[0] < TEMPO_CACHE_SERVICOS:
            return registro[1]

    limite = _geocodificar_distrito(distrito["nome"])
    elementos = _consultar_bairros(limite["bbox"])
    bairros = set()
    identificadores = set()
    for elemento in elementos:
        identificador = (elemento.get("type"), elemento.get("id"))
        if identificador in identificadores:
            continue
        identificadores.add(identificador)
        tags = elemento.get("tags", {})
        if tags.get("place") not in {"suburb", "neighbourhood", "quarter"}:
            continue
        coordenadas = elemento.get("center", elemento)
        try:
            latitude = float(coordenadas["lat"])
            longitude = float(coordenadas["lon"])
        except (KeyError, TypeError, ValueError):
            continue
        if not _ponto_na_geometria(
            longitude, latitude, limite["geometria"]
        ):
            continue
        nome = tags.get("name") or tags.get("name:pt") or tags.get("short_name")
        if isinstance(nome, str) and nome.strip():
            bairros.add(nome.strip()[:100])

    resultado = {
        "distrito": distrito["nome"],
        "codigo_ibge": codigo_distrito,
        "bairros": sorted(bairros, key=str.casefold),
        "fonte": (
            "OpenStreetMap — localidades nomeadas "
            "(place=suburb, place=neighbourhood e place=quarter)"
        ),
        "consultado_em": date.today().isoformat(),
    }
    with _lock_cache_bairros:
        _cache_bairros[codigo_distrito] = (time.monotonic(), resultado)
    return resultado


def _codigo_distrito_da_consulta(consulta):
    parametros = parse_qs(consulta, keep_blank_values=True)
    codigos = parametros.get("distrito", [])
    if len(codigos) != 1:
        raise ValueError("Informe um único código de distrito do IBGE.")
    try:
        codigo = int(codigos[0])
    except ValueError as erro:
        raise ValueError("Código de distrito inválido.") from erro
    codigos_oficiais = {
        distrito["codigo_ibge"] for distrito in carregar_distritos()["distritos"]
    }
    if codigo not in codigos_oficiais:
        raise LookupError("O código informado não corresponde a um distrito.")
    return codigo


def avaliar_entrada(entradas):
    """Usa a mesma validação e classificação do monitor Python."""
    resultado = MonitorRisco().avaliar("WEB", entradas)
    if resultado["ok"]:
        resultado["aviso"] = AVISO
    return resultado


class ServidorAviva(ThreadingHTTPServer):
    """Servidor local com caminhos de dados e arquivos estáticos explícitos."""

    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, endereco, caminho_dados=BASE_CLIMA):
        self.caminho_dados = Path(caminho_dados)
        super().__init__(endereco, ManipuladorAviva)


class ManipuladorAviva(BaseHTTPRequestHandler):
    """Entrega o front-end e as duas rotas locais do protótipo."""

    server_version = "AVIVA"
    sys_version = ""

    def do_GET(self):
        requisicao = urlsplit(self.path)
        if requisicao.path == "/api/clima":
            self._servir_clima(requisicao.query)
            return
        if requisicao.path == "/api/distritos":
            self._servir_distritos()
            return
        if requisicao.path == "/api/bairros":
            self._servir_bairros(requisicao.query)
            return
        if requisicao.path == "/api/servicos":
            self._servir_servicos(requisicao.query)
            return
        if requisicao.path in ARQUIVOS_ESTATICOS:
            self._servir_arquivo(requisicao.path)
            return
        self._responder_json(404, {"erro": "Rota não encontrada."})

    def _servir_distritos(self):
        try:
            dados = carregar_distritos()
        except (OSError, ValueError, json.JSONDecodeError) as erro:
            self.log_error("Falha ao carregar distritos oficiais: %s", erro)
            self._responder_json(
                500,
                {"erro": "Não foi possível carregar a lista oficial de distritos."},
            )
            return
        self._responder_json(200, dados)

    def _servir_servicos(self, consulta):
        try:
            codigo = _codigo_distrito_da_consulta(consulta)
        except ValueError as erro:
            self._responder_json(400, {"erro": str(erro)})
            return
        except LookupError as erro:
            self._responder_json(404, {"erro": str(erro)})
            return
        try:
            dados = carregar_servicos_distrito(codigo)
        except ValueError as erro:
            self._responder_json(404, {"erro": str(erro)})
            return
        except (OSError, TimeoutError, json.JSONDecodeError) as erro:
            self.log_error("Falha ao consultar serviços do distrito: %s", erro)
            self._responder_json(
                502,
                {
                    "erro": (
                        "A fonte aberta de mapas está indisponível agora. "
                        "Tente novamente mais tarde."
                    )
                },
            )
            return
        self._responder_json(200, dados)

    def _servir_bairros(self, consulta):
        try:
            codigo = _codigo_distrito_da_consulta(consulta)
        except ValueError as erro:
            self._responder_json(400, {"erro": str(erro)})
            return
        except LookupError as erro:
            self._responder_json(404, {"erro": str(erro)})
            return
        try:
            dados = carregar_bairros_distrito(codigo)
        except ValueError as erro:
            self._responder_json(404, {"erro": str(erro)})
            return
        except (OSError, TimeoutError, json.JSONDecodeError) as erro:
            self.log_error("Falha ao consultar bairros no OpenStreetMap: %s", erro)
            self._responder_json(
                502,
                {
                    "erro": (
                        "A busca de bairros no OpenStreetMap está indisponível. "
                        "Você ainda pode digitar o bairro manualmente."
                    )
                },
            )
            return
        self._responder_json(200, dados)

    def do_POST(self):
        if urlsplit(self.path).path != "/api/avaliar":
            self._responder_json(404, {"erro": "Rota não encontrada."})
            return

        tamanho = self.headers.get("Content-Length")
        if tamanho is None:
            self._responder_json(411, {"erro": "Content-Length é obrigatório."})
            return
        try:
            tamanho = int(tamanho)
        except ValueError:
            self._responder_json(400, {"erro": "Content-Length inválido."})
            return
        if tamanho < 0:
            self._responder_json(400, {"erro": "Content-Length inválido."})
            return
        if tamanho > TAMANHO_MAXIMO_REQUISICAO:
            self._responder_json(413, {"erro": "Requisição maior que o permitido."})
            return

        try:
            entradas = json.loads(self.rfile.read(tamanho).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._responder_json(400, {"erro": "Corpo deve ser um JSON UTF-8 válido."})
            return
        if not isinstance(entradas, dict):
            self._responder_json(400, {"erro": "Envie um objeto JSON com as leituras."})
            return

        resultado = avaliar_entrada(entradas)
        self._responder_json(200 if resultado["ok"] else 400, resultado)

    def _servir_clima(self, consulta):
        parametros = parse_qs(consulta, keep_blank_values=True)
        valores_dias = parametros.get("dias", ["14"])
        if len(valores_dias) != 1:
            self._responder_json(400, {"erro": "Informe apenas um período."})
            return
        try:
            dias = int(valores_dias[0])
        except ValueError as erro:
            self._responder_json(400, {"erro": str(erro)})
            return
        if not 1 <= dias <= 30:
            self._responder_json(
                400,
                {"erro": "O período solicitado deve estar entre 1 e 30 dias."},
            )
            return
        try:
            dados = carregar_serie_climatica(self.server.caminho_dados, dias=dias)
        except (OSError, ValueError) as erro:
            self.log_error("Falha ao carregar dados climáticos: %s", erro)
            self._responder_json(
                500,
                {"erro": "Não foi possível ler a base climática configurada."},
            )
            return
        self._responder_json(200, dados)

    def _servir_arquivo(self, rota):
        nome, tipo_conteudo = ARQUIVOS_ESTATICOS[rota]
        caminho = WEB_DIR / nome
        try:
            conteudo = caminho.read_bytes()
        except OSError as erro:
            self.log_error("Falha ao ler arquivo estático: %s", erro)
            self._responder_json(500, {"erro": "Não foi possível carregar o painel."})
            return
        self.send_response(200)
        self.send_header("Content-Type", tipo_conteudo)
        self.send_header("Content-Length", str(len(conteudo)))
        self._adicionar_cabecalhos_seguranca()
        self.end_headers()
        self.wfile.write(conteudo)

    def _responder_json(self, status, conteudo):
        corpo = json.dumps(conteudo, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(corpo)))
        self._adicionar_cabecalhos_seguranca()
        self.end_headers()
        self.wfile.write(corpo)

    def _adicionar_cabecalhos_seguranca(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; style-src 'self'; script-src 'self'; "
            "img-src 'self' data:; connect-src 'self'; "
            "frame-src https://www.openstreetmap.org; base-uri 'none'; "
            "form-action 'self'; frame-ancestors 'none'",
        )
        self.send_header("Cache-Control", "no-store")

    def log_message(self, formato, *argumentos):
        """Mantém o log local sem registrar dados enviados pelo usuário."""
        print("%s - %s" % (self.address_string(), formato % argumentos))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    argumentos = parser.parse_args()
    servidor = ServidorAviva((argumentos.host, argumentos.port))
    print(
        "AVIVA disponível em http://%s:%s (somente dados locais; Ctrl+C para encerrar)"
        % (argumentos.host, argumentos.port)
    )
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor AVIVA encerrado.")
    finally:
        servidor.server_close()


if __name__ == "__main__":
    main()

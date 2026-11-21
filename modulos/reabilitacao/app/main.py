"""FastAPI do módulo; independente do app principal AVIVA."""
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from .service import MODALIDADES, load_services, search_services
from .cnes_exploratorio import search_candidates, load_candidates, bairros_disponiveis_sp, load_documented_offices, load_ubs_sp

BASE = Path(__file__).resolve().parents[1]
app = FastAPI(title="AVIVA | Reabilitação", version="0.12.0", description="API informativa de serviços públicos de reabilitação. Não realiza diagnósticos.")
app.mount("/static", StaticFiles(directory=BASE / "web"), name="static")

@app.get("/", include_in_schema=False)
def index():
    return FileResponse(BASE / "web" / "index.html")

@app.get("/api/v1/reabilitacao/health")
def health():
    return {"status": "ok", "modulo": "AVIVA Saúde e Reabilitação", "versao": "0.12.0"}


@app.get("/api/v1/reabilitacao/guia-servicos")
def guia_servicos():
    """Conteúdo educativo para futura integração com app principal.

    Informações gerais; não substituem validação de serviços individuais.
    """
    return {
      "servicos": [
        {"id":"ubs","sigla":"UBS","nome":"Unidade Básica de Saúde","papel":"Atenção inicial e acompanhamento","oferece":"Avaliação inicial, acompanhamento, orientações e encaminhamentos; algumas unidades também oferecem ações de reabilitação.","acesso":"Em geral, pode ser procurada diretamente. A UBS de referência pode depender do endereço de moradia.","aviso":"Nem todas têm fisioterapia ou terapia ocupacional no local."},
        {"id":"cer","sigla":"CER","nome":"Centro Especializado em Reabilitação","papel":"Reabilitação especializada","oferece":"Reabilitação física, auditiva, visual e/ou intelectual, conforme a habilitação.","acesso":"A rede de saúde costuma organizar a avaliação e o encaminhamento.","aviso":"Nem todo CER possui as quatro modalidades."},
        {"id":"caps","sigla":"CAPS","nome":"Centro de Atenção Psicossocial","papel":"Saúde mental e atenção psicossocial","oferece":"Acolhimento, acompanhamento multiprofissional e cuidado em saúde mental, conforme o tipo de CAPS.","acesso":"Procura direta para o primeiro acolhimento, sem encaminhamento obrigatório.","aviso":"A equipe avalia o cuidado adequado após o acolhimento."},
        {"id":"oficina","sigla":"Oficina Ortopédica","nome":"Oficina Ortopédica","papel":"Órteses, próteses e meios auxiliares","oferece":"Confecção, fornecimento, adaptação e manutenção de recursos assistivos, conforme o serviço.","acesso":"Geralmente depende de avaliação e indicação de profissional habilitado.","aviso":"Os dispositivos não são escolhidos livremente como produtos de catálogo."}
      ],
      "fontes": [
        "https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/s/saude-da-pessoa-com-deficiencia/rcpd",
        "https://www.gov.br/saude/pt-br/composicao/saes/desmad/raps/caps/caps/",
        "https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/s/saude-da-pessoa-com-deficiencia/faq/o-que-e-uma-oficina"
      ],
      "aviso":"Conteúdo educativo geral; não confirma serviços, horários ou vagas em uma unidade específica."
    }

@app.get("/api/v1/reabilitacao/fluxo-acesso")
def fluxo_acesso():
    return {"passos":[
      {"ordem":1,"titulo":"Percebi uma dificuldade","descricao":"Reconheço que uma atividade do dia a dia ficou difícil."},
      {"ordem":2,"titulo":"Busco orientação","descricao":"Posso procurar uma UBS para conversar e receber orientação inicial."},
      {"ordem":3,"titulo":"Recebo uma avaliação","descricao":"A equipe de saúde escuta, avalia e orienta o cuidado."},
      {"ordem":4,"titulo":"Encaminhamento, quando necessário","descricao":"A rede indica outro serviço de acordo com a necessidade."},
      {"ordem":5,"titulo":"Começo o cuidado indicado","descricao":"O cuidado pode incluir acompanhamento, reabilitação ou recurso assistivo."},
      {"ordem":6,"titulo":"Continuo meu acompanhamento","descricao":"Há retornos e reavaliações quando necessários."}],
      "excecoes":[
        {"tipo":"caps","mensagem":"O CAPS aceita procura direta para primeiro acolhimento, sem encaminhamento obrigatório."},
        {"tipo":"urgencia","mensagem":"Em emergência, procure urgência ou acione o SAMU 192. Não siga uma fila de atendimento rotineiro."}
      ],
      "aviso":"Caminho geral educativo, que pode variar conforme o caso e a rede local."
    }

@app.get("/api/v1/reabilitacao/modalidades")
def modalities():
    return {"modalidades": [{"id": "fisica", "titulo": "Reabilitação física"}, {"id": "auditiva", "titulo": "Reabilitação auditiva"}, {"id": "visual", "titulo": "Reabilitação visual"}, {"id": "intelectual", "titulo": "Reabilitação intelectual"}],
            "observacao": "Reabilitação cognitiva pode ser ofertada em diferentes serviços; não é uma quinta modalidade oficial de CER."}

@app.get("/api/v1/reabilitacao/servicos")
def services(uf: str | None = Query(default=None, min_length=2, max_length=2),
             municipio: str | None = Query(default=None, max_length=90),
             modalidade: str | None = Query(default=None)):
    try:
        results = search_services(uf=uf, municipio=municipio, modalidade=modalidade)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    loaded = load_services()
    return {"total": len(results), "resultados": results,
            "situacao_base": "registros_conferidos" if loaded else "sem_registros_conferidos",
            "aviso": "A ausência de resultados não comprova ausência de serviços. Consulte a UBS ou secretaria municipal de saúde.",
            "fonte_principal": "https://dadosabertos.saude.gov.br/dataset/cnes-cadastro-nacional-de-estabelecimentos-de-saude"}

@app.get("/api/v1/reabilitacao/orientacoes")
def guidance():
    return {"passos": [
        {"titulo": "Comece pela UBS", "descricao": "A unidade básica de saúde é uma porta de entrada habitual para avaliação e encaminhamento conforme a rede local."},
        {"titulo": "Explique sua necessidade", "descricao": "Relate dificuldades funcionais e informações relevantes diretamente à equipe de saúde, sem diagnóstico pelo aplicativo."},
        {"titulo": "Confirme o encaminhamento", "descricao": "A secretaria municipal e a rede de regulação orientam o acesso a serviços especializados, quando indicado."},
        {"titulo": "Confirme antes de se deslocar", "descricao": "O cadastro de estabelecimentos não garante vaga, agenda ou modalidade ativa na data da visita."}],
        "fonte": "https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/s/saude-da-pessoa-com-deficiencia/rcpd"}


@app.get("/api/v1/reabilitacao/cnes/candidatos")
def cnes_candidates(uf: str | None = Query(None, min_length=2, max_length=2),
                    municipio: str | None = Query(None, max_length=90),
                    categoria: str | None = Query(None),
                    limite: int = Query(30, ge=1, le=100),
                    pagina: int = Query(1, ge=1, le=10000),
                    zona: str | None = Query(None),
                    bairro: str | None = Query(None, max_length=100)):
    """Busca exploratória; nunca interpretar como serviço habilitado do SUS."""
    try:
        data = search_candidates(uf=uf, municipio=municipio, categoria=categoria, limite=limite, pagina=pagina, zona=zona, bairro=bairro)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    data['situacao_base'] = 'cnes_com_oficinas_e_ubs_sp'
    data['aviso'] = ('UBS identificadas pelo tipo cadastral e nome no CNES; outras categorias são indícios por nome ou oficinas com fontes institucionais. '
                     'A presença no cadastro não confirma reabilitação especializada, disponibilidade, agenda nem UBS de referência. ')
    return data

@app.get("/api/v1/reabilitacao/cnes/bairros-sp")
def cnes_bairros_sp(zona: str | None = Query(None),
                    categoria: str | None = Query(None)):
    """Opções para filtro de bairro em São Paulo (capital)."""
    try:
        return bairros_disponiveis_sp(zona=zona, categoria=categoria)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

@app.get("/api/v1/reabilitacao/cnes/resumo")
def cnes_summary():
    from collections import Counter
    data = load_candidates()
    counts = Counter(r['categoria_indicio_nome'] for r in data)
    flags = Counter(r['ambulatorial_sus_informado'] for r in data)
    return {'total_estabelecimentos_cnes_na_fonte':642608,
            'total_candidatos_por_nome':len(data), 'categorias_indiciarias':dict(counts),
            'indicador_ambulatorial_sus':dict(flags),
            'oficinas_com_documentacao_institucional_sp':len(load_documented_offices()),
            'ubs_sp_por_tipo_e_nome':len(load_ubs_sp()),
            'aviso':'Números não equivalem à oferta confirmada de reabilitação. Nomes usados como pista.'}

@app.get("/api/v1/reabilitacao/cnes/mapa-sp")
def cnes_mapa_sp(zona: str | None = Query(None),
                 bairro: str | None = Query(None, max_length=100),
                 categoria: str | None = Query(None),
                 modo: str = Query('todos')):
    """Mapa com pontos conferidos e exploratórios claramente sinalizados.

    A localização do cidadão NÃO é recebida por este endpoint.
    """
    from .geografia import pontos_sp
    try:
        return pontos_sp(zona=zona, bairro=bairro, categoria=categoria, modo=modo)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

@app.get("/api/v1/reabilitacao/cnes/auditoria-geografica/resumo")
def cnes_resumo_auditoria():
    from .geografia import audit_summary
    return audit_summary()

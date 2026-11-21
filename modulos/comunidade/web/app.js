/* AVIVA | Interface do módulo Comunidade: histórico de chuva, território e simulação. */
"use strict";

const chartSvgNamespace = "http://www.w3.org/2000/svg";
const communityStorageKey = "aviva-demo-publicacoes-v1";
const state = {
  stations: [],
  selectedStation: "",
  metric: "chuva_dia_mm",
  districts: [],
  selectedDistrict: null,
  selectedNeighborhood: "",
  neighborhoodRequestId: 0,
  posts: [],
  services: null,
  serviceFilter: "todos",
  serviceRequestId: 0,
};

const elements = {
  stationCount: document.getElementById("station-count"),
  observationCount: document.getElementById("observation-count"),
  latestDate: document.getElementById("latest-date"),
  sourceName: document.getElementById("source-name"),
  stationSwitch: document.getElementById("station-switch"),
  chartTitle: document.getElementById("chart-title"),
  chartPeriod: document.getElementById("chart-period"),
  chartMetricLabel: document.getElementById("chart-metric-label"),
  chartStationFooter: document.getElementById("chart-station-footer"),
  chart: document.getElementById("rain-chart"),
  latestRain: document.getElementById("latest-rain"),
  latestContext: document.getElementById("latest-context"),
  form: document.getElementById("simulation-form"),
  formError: document.getElementById("form-error"),
  resultPlaceholder: document.getElementById("result-placeholder"),
  resultContent: document.getElementById("result-content"),
  resultLevel: document.getElementById("result-level"),
  resultSummary: document.getElementById("result-summary"),
  resultReadings: document.getElementById("result-readings"),
  recommendations: document.getElementById("recommendations"),
  resultWarning: document.getElementById("result-warning"),
  territoryForm: document.getElementById("territory-form"),
  districtSelect: document.getElementById("district-select"),
  neighborhoodInput: document.getElementById("neighborhood-input"),
  territoryError: document.getElementById("territory-error"),
  districtSource: document.getElementById("district-source"),
  communitySection: document.getElementById("mural"),
  communityStorage: document.getElementById("community-storage-status"),
  selectedRegion: document.getElementById("selected-region"),
  changeRegion: document.getElementById("change-region"),
  territoryMap: document.getElementById("territory-map"),
  mapPlaceholder: document.getElementById("map-placeholder"),
  mapTitle: document.getElementById("map-title"),
  openMapLink: document.getElementById("open-map-link"),
  mapFallbackLink: document.getElementById("map-fallback-link"),
  territoryInsights: document.getElementById("territory-insights"),
  territoryStats: document.getElementById("territory-stats"),
  placesStatus: document.getElementById("places-status"),
  placesFilters: document.getElementById("places-filters"),
  placesHeading: document.getElementById("places-heading"),
  placeList: document.getElementById("place-list"),
  placesEmpty: document.getElementById("places-empty"),
  placesMapFallback: document.getElementById("places-map-fallback"),
  retryServices: document.getElementById("retry-services"),
  postForm: document.getElementById("post-form"),
  postCategory: document.getElementById("post-category"),
  postNeighborhood: document.getElementById("post-neighborhood"),
  neighborhoodOptions: document.getElementById("neighborhood-options"),
  neighborhoodSuggestions: document.getElementById("neighborhood-suggestions"),
  neighborhoodSource: document.getElementById("neighborhood-source"),
  postTitle: document.getElementById("post-title"),
  postDescription: document.getElementById("post-description"),
  postError: document.getElementById("post-error"),
  postFilter: document.getElementById("post-filter"),
  postList: document.getElementById("post-list"),
  feedCount: document.getElementById("feed-count"),
  emptyFeed: document.getElementById("empty-feed"),
};

function criarElementoSvg(nome, atributos) {
  const elemento = document.createElementNS(chartSvgNamespace, nome);
  Object.entries(atributos).forEach(([chave, valor]) => {
    elemento.setAttribute(chave, String(valor));
  });
  return elemento;
}

function formatarData(valor) {
  const [ano, mes, dia] = valor.split("-").map(Number);
  return new Intl.DateTimeFormat("pt-BR", {
    day: "2-digit",
    month: "short",
    timeZone: "UTC",
  }).format(new Date(Date.UTC(ano, mes - 1, dia)));
}

function formatarNumero(valor, casas = 1) {
  return new Intl.NumberFormat("pt-BR", {
    maximumFractionDigits: casas,
  }).format(valor);
}

function obterEstacaoSelecionada() {
  return state.stations.find((station) => station.codigo === state.selectedStation);
}

function mostrarErroDoGrafico(mensagem) {
  elements.chart.replaceChildren();
  const texto = criarElementoSvg("text", {
    x: 380,
    y: 145,
    "text-anchor": "middle",
    class: "chart-empty",
  });
  texto.textContent = mensagem;
  elements.chart.append(texto);
}

function desenharGrafico(estacao) {
  if (!estacao || !Array.isArray(estacao.serie) || estacao.serie.length === 0) {
    mostrarErroDoGrafico("Sem observações disponíveis para esta estação.");
    return;
  }

  const largura = 760;
  const altura = 292;
  const margem = { top: 18, right: 15, bottom: 42, left: 48 };
  const larguraGrafico = largura - margem.left - margem.right;
  const alturaGrafico = altura - margem.top - margem.bottom;
  const valorChuva = state.metric === "chuva_dia_mm";
  const chaveValor = state.metric;
  const valores = estacao.serie.map((registro) => Number(registro[chaveValor]));
  const maior = Math.max(...valores, 1);
  const passoEixo = maior > 20 ? 20 : maior > 8 ? 5 : maior > 4 ? 2 : 1;
  const topoEixo = Math.ceil(maior / passoEixo) * passoEixo || passoEixo;
  const coordenadaX = (indice) =>
    margem.left +
    (estacao.serie.length <= 1
      ? larguraGrafico / 2
      : (indice / (estacao.serie.length - 1)) * larguraGrafico);
  const coordenadaY = (valor) =>
    margem.top + alturaGrafico - (valor / topoEixo) * alturaGrafico;

  elements.chart.replaceChildren();
  elements.chart.setAttribute(
    "aria-label",
    `${valorChuva ? "Precipitação diária em milímetros" : "Horas com chuva"} para ${estacao.nome}, últimos ${estacao.serie.length} dias disponíveis`,
  );

  for (let passo = 0; passo <= 4; passo += 1) {
    const valor = (topoEixo * passo) / 4;
    const y = coordenadaY(valor);
    elements.chart.append(
      criarElementoSvg("line", {
        x1: margem.left,
        x2: largura - margem.right,
        y1: y,
        y2: y,
        class: "chart-grid",
      }),
    );
    const rotulo = criarElementoSvg("text", {
      x: margem.left - 10,
      y: y + 3,
      "text-anchor": "end",
      class: "chart-axis-label",
    });
    rotulo.textContent = formatarNumero(valor, 0);
    elements.chart.append(rotulo);
  }

  const pontos = estacao.serie.map((registro, indice) => [
    coordenadaX(indice),
    coordenadaY(Number(registro[chaveValor])),
  ]);
  const caminho = pontos
    .map(([x, y], indice) => `${indice === 0 ? "M" : "L"} ${x} ${y}`)
    .join(" ");
  const area = `${caminho} L ${pontos[pontos.length - 1][0]} ${
    margem.top + alturaGrafico
  } L ${pontos[0][0]} ${margem.top + alturaGrafico} Z`;
  elements.chart.append(
    criarElementoSvg("path", { d: area, class: "chart-area" }),
    criarElementoSvg("path", { d: caminho, class: "chart-line" }),
  );

  estacao.serie.forEach((registro, indice) => {
    const [x, y] = pontos[indice];
    const ponto = criarElementoSvg("circle", {
      cx: x,
      cy: y,
      r: indice === pontos.length - 1 ? 5 : 3.3,
      class: `chart-point${indice === pontos.length - 1 ? " latest" : ""}`,
    });
    const dica = criarElementoSvg("title", {});
    dica.textContent = `${formatarData(registro.data)} · ${formatarNumero(
      Number(registro[chaveValor]),
      1,
    )} ${valorChuva ? "mm" : "h"}`;
    ponto.append(dica);
    elements.chart.append(ponto);
  });

  const indicesRotulados = [...new Set([0, Math.floor((pontos.length - 1) / 2), pontos.length - 1])];
  indicesRotulados.forEach((indice) => {
    const rotulo = criarElementoSvg("text", {
      x: coordenadaX(indice),
      y: altura - 12,
      "text-anchor": indice === 0 ? "start" : indice === pontos.length - 1 ? "end" : "middle",
      class: "chart-axis-label",
    });
    rotulo.textContent = formatarData(estacao.serie[indice].data);
    elements.chart.append(rotulo);
  });

  elements.chartTitle.textContent = estacao.nome;
  elements.chartPeriod.textContent = `Últimas ${estacao.serie.length} observações diárias disponíveis`;
  elements.chartMetricLabel.textContent = valorChuva ? "mm por dia" : "horas por dia";
  elements.chartStationFooter.textContent = `${estacao.codigo} · ${estacao.total_observacoes} dias completos`;
  elements.latestRain.replaceChildren(
    document.createTextNode(formatarNumero(estacao.ultima_chuva_mm, 1)),
  );
  const unidade = document.createElement("small");
  unidade.textContent = " mm";
  elements.latestRain.append(unidade);
  elements.latestContext.textContent = `${formatarData(
    estacao.ultima_data,
  )} · ${estacao.nome} (${estacao.codigo})`;
}

function renderizarBotoesEstacao() {
  elements.stationSwitch.replaceChildren();
  state.stations.forEach((estacao) => {
    const botao = document.createElement("button");
    botao.type = "button";
    botao.className = `station-button${
      estacao.codigo === state.selectedStation ? " is-selected" : ""
    }`;
    botao.textContent = estacao.nome.replace("São Paulo — ", "");
    botao.setAttribute("aria-pressed", String(estacao.codigo === state.selectedStation));
    botao.addEventListener("click", () => {
      state.selectedStation = estacao.codigo;
      renderizarBotoesEstacao();
      desenharGrafico(obterEstacaoSelecionada());
    });
    elements.stationSwitch.append(botao);
  });
}

async function carregarClima() {
  elements.sourceName.textContent = "CARREGANDO DADOS · INMET";
  try {
    const resposta = await fetch("/api/clima?dias=14", {
      headers: { Accept: "application/json" },
    });
    const dados = await resposta.json();
    if (!resposta.ok) {
      throw new Error(dados.erro || "Não foi possível carregar a base climática.");
    }
    if (!Array.isArray(dados.estacoes) || dados.estacoes.length === 0) {
      throw new Error("A base não contém estações com observações.");
    }
    state.stations = dados.estacoes;
    state.selectedStation = dados.estacoes[0].codigo;
    elements.stationCount.textContent = String(dados.estacoes.length).padStart(2, "0");
    elements.observationCount.textContent = new Intl.NumberFormat("pt-BR").format(
      dados.total_observacoes,
    );
    elements.latestDate.textContent = formatarData(dados.ultima_observacao);
    elements.sourceName.textContent = "FONTE OFICIAL · INMET";
    renderizarBotoesEstacao();
    desenharGrafico(obterEstacaoSelecionada());
  } catch (erro) {
    elements.sourceName.textContent = "DADOS INDISPONÍVEIS";
    elements.chartTitle.textContent = "Não foi possível carregar as observações";
    elements.latestDate.textContent = "Indisponível";
    elements.stationCount.textContent = "—";
    elements.observationCount.textContent = "—";
    elements.latestRain.textContent = "—";
    elements.latestContext.textContent = erro.message;
    mostrarErroDoGrafico("Verifique se o servidor AVIVA está conectado à base CSV.");
  }
}

function selecionarIndicador(botaoSelecionado) {
  document.querySelectorAll(".metric-button").forEach((botao) => {
    const selecionado = botao === botaoSelecionado;
    botao.classList.toggle("is-selected", selecionado);
    botao.setAttribute("aria-pressed", String(selecionado));
  });
  state.metric = botaoSelecionado.dataset.metric;
  desenharGrafico(obterEstacaoSelecionada());
}

function exibirErroFormulario(mensagem) {
  elements.formError.textContent = mensagem;
  elements.formError.hidden = false;
}

function renderizarResultado(resultado) {
  elements.resultPlaceholder.hidden = true;
  elements.resultContent.hidden = false;
  elements.formError.hidden = true;
  elements.resultLevel.textContent = resultado.nivel;
  elements.resultLevel.className = "result-level";
  if (resultado.nivel === "ATENÇÃO") {
    elements.resultLevel.classList.add("is-attention");
  } else if (resultado.nivel === "CRÍTICO") {
    elements.resultLevel.classList.add("is-critical");
  }
  elements.resultSummary.textContent =
    "Classificação baseada nas regras provisórias do monitor Python.";
  elements.resultReadings.replaceChildren();
  Object.entries(resultado.leituras).forEach(([variavel, valor]) => {
    const configuracao = {
      nivel_agua_cm: ["Nível da água", "cm"],
      chuva_mm_h: ["Chuva", "mm/h"],
    }[variavel];
    if (!configuracao) {
      return;
    }
    const detalhe = document.createElement("span");
    detalhe.className = "reading-chip";
    detalhe.textContent = `${configuracao[0]} · ${formatarNumero(
      valor,
      1,
    )} ${configuracao[1]} — ${resultado.detalhes[variavel]}`;
    elements.resultReadings.append(detalhe);
  });
  elements.recommendations.replaceChildren();
  resultado.recomendacoes.forEach((recomendacao) => {
    const item = document.createElement("li");
    item.textContent = recomendacao;
    elements.recommendations.append(item);
  });
  elements.resultWarning.textContent = resultado.aviso;
}

async function avaliarSimulacao(evento) {
  evento.preventDefault();
  elements.formError.hidden = true;
  const formData = new FormData(elements.form);
  const entradas = {
    nivel_agua_cm: formData.get("nivel_agua_cm"),
    chuva_mm_h: formData.get("chuva_mm_h"),
  };
  try {
    const resposta = await fetch("/api/avaliar", {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(entradas),
    });
    const resultado = await resposta.json();
    if (!resposta.ok) {
      throw new Error((resultado.erros || [resultado.erro]).filter(Boolean).join(" "));
    }
    renderizarResultado(resultado);
  } catch (erro) {
    exibirErroFormulario(erro.message || "Não foi possível executar a simulação local.");
  }
}

function normalizarTexto(valor) {
  return valor
    .normalize("NFD")
    .replace(/\p{Diacritic}/gu, "")
    .trim()
    .toLocaleLowerCase("pt-BR");
}

async function carregarDistritos() {
  elements.districtSource.textContent = "Carregando a lista oficial do IBGE…";
  try {
    const resposta = await fetch("/api/distritos", {
      headers: { Accept: "application/json" },
    });
    const dados = await resposta.json();
    if (!resposta.ok) {
      throw new Error(dados.erro || "Não foi possível carregar os distritos.");
    }
    if (
      !Array.isArray(dados.distritos) ||
      dados.distritos.length !== 96 ||
      !dados.distritos.every(
        (distrito) =>
          Number.isInteger(distrito.codigo_ibge) &&
          typeof distrito.nome === "string" &&
          distrito.nome.trim(),
      )
    ) {
      throw new Error("A lista de distritos retornada pelo servidor é inválida.");
    }

    state.districts = dados.distritos;
    elements.districtSelect.replaceChildren(new Option("Selecione seu distrito", ""));
    state.districts.forEach((district) => {
      elements.districtSelect.add(
        new Option(district.nome, String(district.codigo_ibge)),
      );
    });
    elements.districtSelect.disabled = false;
    elements.territoryForm.querySelector('button[type="submit"]').disabled = false;
    elements.districtSource.textContent = `${dados.fonte} · ${dados.consultado_em.slice(
      0,
      10,
    )}`;
  } catch (erro) {
    elements.districtSource.textContent = erro.message;
    elements.territoryError.textContent =
      "A lista oficial não carregou. Tente novamente depois de verificar o servidor.";
    elements.territoryError.hidden = false;
  }
}

function atualizarMapa(servicos) {
  const { bbox, centro } = servicos;
  const urlMapa = new URL(
    "https://www.openstreetmap.org/export/embed.html",
  );
  urlMapa.searchParams.set(
    "bbox",
    [bbox.oeste, bbox.sul, bbox.leste, bbox.norte].join(","),
  );
  urlMapa.searchParams.set("layer", "mapnik");
  urlMapa.searchParams.set(
    "marker",
    `${centro.latitude},${centro.longitude}`,
  );
  elements.territoryMap.src = urlMapa.toString();
  elements.mapPlaceholder.hidden = true;
  elements.openMapLink.href = `https://www.openstreetmap.org/#map=14/${centro.latitude}/${centro.longitude}`;
  elements.mapFallbackLink.href = elements.openMapLink.href;
  elements.placesMapFallback.href = elements.openMapLink.href;
  elements.placesMapFallback.hidden = true;
  elements.mapTitle.textContent = servicos.distrito;
}

function aplicarTerritorio(evento) {
  evento.preventDefault();
  elements.territoryError.hidden = true;
  const district = state.districts.find(
    (item) => String(item.codigo_ibge) === elements.districtSelect.value,
  );
  if (!district) {
    elements.territoryError.textContent = "Escolha um distrito válido.";
    elements.territoryError.hidden = false;
    return;
  }

  state.selectedDistrict = district;
  state.selectedNeighborhood = elements.neighborhoodInput.value
    .trim()
    .replace(/\s+/g, " ");
  elements.selectedRegion.textContent = state.selectedNeighborhood
    ? `${state.selectedNeighborhood} · ${district.nome} · São Paulo`
    : `${district.nome} · São Paulo`;
  const buscaMapa = new URL("https://www.openstreetmap.org/search");
  buscaMapa.searchParams.set("query", `${district.nome}, São Paulo, SP`);
  elements.mapTitle.textContent = `${district.nome} · São Paulo`;
  elements.openMapLink.href = buscaMapa.toString();
  elements.mapFallbackLink.href = buscaMapa.toString();
  elements.mapFallbackLink.textContent = `Buscar ${district.nome} no OpenStreetMap ↗`;
  elements.territoryInsights.hidden = false;
  elements.postNeighborhood.value = state.selectedNeighborhood;
  renderizarPublicacoes();
  carregarBairros(district);
  carregarServicos(district);
  elements.communitySection.scrollIntoView({ behavior: "smooth", block: "start" });
}

function renderizarSugestoesDeBairro(bairros) {
  elements.neighborhoodOptions.replaceChildren();
  elements.neighborhoodSuggestions.replaceChildren();
  elements.neighborhoodSuggestions.hidden = bairros.length === 0;
  bairros.forEach((bairro) => {
    elements.neighborhoodOptions.append(new Option(bairro, bairro));
    const sugestao = document.createElement("button");
    sugestao.className = "neighborhood-suggestion";
    sugestao.type = "button";
    sugestao.textContent = bairro;
    sugestao.addEventListener("click", () => {
      elements.neighborhoodInput.value = bairro;
      elements.neighborhoodInput.focus();
    });
    elements.neighborhoodSuggestions.append(sugestao);
  });
  elements.neighborhoodSource.textContent = bairros.length
    ? `${bairros.length} bairro(s) ou localidades encontrados em objetos geográficos do OpenStreetMap. A lista é colaborativa, pode estar incompleta e não é oficial.`
    : "A fonte não encontrou localidades nomeadas neste distrito. Você pode digitar o nome; não informe endereço.";
}

function formatarDistancia(distancia) {
  return new Intl.NumberFormat("pt-BR", {
    maximumFractionDigits: 1,
  }).format(distancia);
}

function renderizarResumoServicos(servicos) {
  elements.territoryStats.replaceChildren();
  const statPublicos = document.createElement("article");
  statPublicos.className = "territory-stat stat-governo";
  const quantidadePublicos = document.createElement("strong");
  quantidadePublicos.textContent = String(servicos.contagem_publicos || 0);
  const labelPublicos = document.createElement("span");
  labelPublicos.textContent = "Gestão pública indicada";
  statPublicos.append(quantidadePublicos, labelPublicos);
  elements.territoryStats.append(statPublicos);

  Object.entries(servicos.categorias).forEach(([categoria, nome]) => {
    const stat = document.createElement("article");
    stat.className = `territory-stat stat-${categoria}`;
    const quantidade = document.createElement("strong");
    quantidade.textContent = String(
      servicos.contagem_por_categoria[categoria] || 0,
    );
    const label = document.createElement("span");
    label.textContent = nome;
    stat.append(quantidade, label);
    elements.territoryStats.append(stat);
  });
}

function selecionarFiltroServicos(filtro) {
  state.serviceFilter = filtro;
  elements.placesFilters.querySelectorAll("button").forEach((botao) => {
    const selecionado = botao.dataset.category === filtro;
    botao.classList.toggle("is-selected", selecionado);
    botao.setAttribute("aria-pressed", String(selecionado));
  });
  renderizarListaServicos();
}

function renderizarFiltrosServicos(servicos) {
  elements.placesFilters.replaceChildren();
  const filtros = [
    ["todos", "Todos", servicos.total],
    ["publicos", "Gestão pública indicada", servicos.contagem_publicos || 0],
    ...Object.entries(servicos.categorias).map(([categoria, nome]) => [
      categoria,
      nome,
      servicos.contagem_por_categoria[categoria] || 0,
    ]),
  ];
  filtros.forEach(([categoria, nome, quantidade]) => {
    const botao = document.createElement("button");
    botao.type = "button";
    botao.className = `places-filter${
      categoria === state.serviceFilter ? " is-selected" : ""
    }`;
    botao.dataset.category = categoria;
    botao.setAttribute(
      "aria-pressed",
      String(categoria === state.serviceFilter),
    );
    botao.textContent = `${nome} ${quantidade}`;
    botao.addEventListener("click", () =>
      selecionarFiltroServicos(categoria),
    );
    elements.placesFilters.append(botao);
  });
}

function renderizarListaServicos() {
  if (!state.services) {
    return;
  }
  const pontos =
    state.serviceFilter === "todos"
      ? state.services.pontos
      : state.serviceFilter === "publicos"
        ? state.services.pontos.filter(
            (ponto) => ponto.gestao_publica_indicada,
          )
      : state.services.pontos.filter(
          (ponto) => ponto.categoria === state.serviceFilter,
        );
  elements.placeList.replaceChildren();
  elements.placesHeading.textContent =
    state.serviceFilter === "todos"
      ? "Serviços e espaços próximos"
      : state.serviceFilter === "publicos"
        ? "Órgãos e serviços com gestão pública indicada"
        : state.services.categorias[state.serviceFilter];
  elements.placesEmpty.hidden = pontos.length > 0;
  pontos.forEach((ponto) => {
    const item = document.createElement("article");
    item.className = "place-card";

    const details = document.createElement("div");
    details.className = "place-details";
    const heading = document.createElement("div");
    heading.className = "place-title-row";
    const title = document.createElement("h5");
    title.textContent = ponto.nome;
    const category = document.createElement("span");
    category.className = `place-kind kind-${ponto.categoria}`;
    category.textContent = ponto.tipo;
    heading.append(title, category);

    const location = document.createElement("p");
    location.className = "place-location";
    location.textContent = ponto.endereco || "Endereço não informado no mapa";
    const management = document.createElement("p");
    management.className = "place-management";
    if (ponto.operador) {
      management.textContent = `Operador no cadastro: ${ponto.operador}`;
    } else {
      management.textContent = "Tipo de gestão não informado pela fonte";
    }
    if (ponto.gestao_publica_indicada) {
      const publicBadge = document.createElement("span");
      publicBadge.className = "place-public-badge";
      publicBadge.textContent = "Gestão pública indicada";
      management.append(" · ", publicBadge);
    }

    const meta = document.createElement("p");
    meta.className = "place-distance";
    meta.textContent = `${formatarDistancia(
      ponto.distancia_centro_km,
    )} km do centro aproximado do distrito`;

    const link = document.createElement("a");
    link.className = "place-map-link";
    link.href = ponto.osm_url;
    link.target = "_blank";
    link.rel = "noreferrer";
    link.textContent = "Ver no mapa ↗";
    details.append(heading, location, management, meta);
    item.append(details, link);
    elements.placeList.append(item);
  });
}

async function carregarServicos(district) {
  const requestId = ++state.serviceRequestId;
  state.services = null;
  state.serviceFilter = "todos";
  elements.territoryInsights.hidden = false;
  elements.placesStatus.textContent =
    "Consultando pontos de referência mapeados no OpenStreetMap…";
  elements.retryServices.hidden = true;
  elements.territoryStats.replaceChildren();
  elements.placesFilters.replaceChildren();
  elements.placeList.replaceChildren();
  elements.placesEmpty.hidden = true;
  elements.mapPlaceholder.hidden = false;
  elements.mapPlaceholder.querySelector("p").textContent =
    "Carregando o limite do distrito e os serviços mapeados…";

  try {
    const resposta = await fetch(
      `/api/servicos?distrito=${encodeURIComponent(district.codigo_ibge)}`,
      { headers: { Accept: "application/json" } },
    );
    const dados = await resposta.json();
    if (!resposta.ok) {
      throw new Error(dados.erro || "Não foi possível consultar os serviços.");
    }
    if (
      dados.codigo_ibge !== district.codigo_ibge ||
      !Array.isArray(dados.pontos) ||
      !dados.categorias ||
      !dados.contagem_por_categoria ||
      !Number.isInteger(dados.contagem_publicos)
    ) {
      throw new Error("A fonte retornou dados territoriais incompletos.");
    }
    if (requestId !== state.serviceRequestId) {
      return;
    }
    state.services = dados;
    atualizarMapa(dados);
    renderizarResumoServicos(dados);
    renderizarFiltrosServicos(dados);
    renderizarListaServicos();
    elements.placesStatus.textContent =
      dados.total > dados.pontos.length
        ? `${dados.pontos.length} de ${dados.total} locais mapeados · consulta ${dados.consultado_em}`
        : `${dados.total} local(is) mapeados · consulta ${dados.consultado_em}`;
    if (dados.total === 0) {
      elements.placesStatus.textContent =
        "Nenhum ponto cadastrado pela fonte para este distrito.";
      elements.mapPlaceholder.querySelector("p").textContent =
        "Não foi possível desenhar o mapa para esta região.";
      elements.mapPlaceholder.hidden = false;
    }
  } catch (erro) {
    if (requestId !== state.serviceRequestId) {
      return;
    }
    elements.placesStatus.textContent = erro.message;
    elements.neighborhoodOptions.replaceChildren();
    elements.neighborhoodSuggestions.replaceChildren();
    elements.neighborhoodSuggestions.hidden = true;
    elements.neighborhoodSource.textContent =
      "A fonte de mapas não respondeu. Você ainda pode digitar o nome do bairro; não informe endereço.";
    elements.placesEmpty.hidden = false;
    elements.placesMapFallback.hidden = false;
    const buscaMapa = new URL("https://www.openstreetmap.org/search");
    buscaMapa.searchParams.set(
      "query",
      `${district.nome}, São Paulo, SP`,
    );
    elements.placesMapFallback.href = buscaMapa.toString();
    elements.placesEmpty.querySelector("p").textContent =
      "O catálogo aberto está indisponível. Não exibimos locais estimados; tente novamente ou abra a busca do distrito no mapa.";
    elements.retryServices.hidden = false;
    elements.mapPlaceholder.querySelector("p").textContent =
      "Mapa indisponível: não foi possível validar o limite deste distrito.";
    elements.mapPlaceholder.hidden = false;
  }
}

async function carregarBairros(district) {
  const requestId = ++state.neighborhoodRequestId;
  elements.neighborhoodOptions.replaceChildren();
  elements.neighborhoodSuggestions.replaceChildren();
  elements.neighborhoodSuggestions.hidden = true;
  elements.neighborhoodSource.textContent =
    "Buscando localidades nomeadas no OpenStreetMap…";

  try {
    const resposta = await fetch(
      `/api/bairros?distrito=${encodeURIComponent(district.codigo_ibge)}`,
      { headers: { Accept: "application/json" } },
    );
    const dados = await resposta.json();
    if (!resposta.ok) {
      throw new Error(dados.erro || "Não foi possível consultar os bairros.");
    }
    if (
      dados.codigo_ibge !== district.codigo_ibge ||
      !Array.isArray(dados.bairros) ||
      !dados.bairros.every(
        (bairro) => typeof bairro === "string" && bairro.trim(),
      )
    ) {
      throw new Error("A fonte retornou uma lista de bairros inválida.");
    }
    if (requestId !== state.neighborhoodRequestId) {
      return;
    }
    renderizarSugestoesDeBairro(dados.bairros);
  } catch (erro) {
    if (requestId !== state.neighborhoodRequestId) {
      return;
    }
    elements.neighborhoodOptions.replaceChildren();
    elements.neighborhoodSuggestions.replaceChildren();
    elements.neighborhoodSuggestions.hidden = true;
    elements.neighborhoodSource.textContent =
      `${erro.message} Digite o nome do bairro; não informe rua, número ou endereço.`;
  }
}

function publicacoesVisiveis() {
  if (!state.selectedDistrict) {
    return [];
  }
  const filtro = elements.postFilter.value;
  const bairroSelecionado = normalizarTexto(state.selectedNeighborhood);
  return state.posts.filter((post) => {
    if (post.codigoDistrito !== state.selectedDistrict.codigo_ibge) {
      return false;
    }
    if (filtro !== "todas" && post.categoria !== filtro) {
      return false;
    }
    return (
      !bairroSelecionado ||
      normalizarTexto(post.bairro) === bairroSelecionado
    );
  });
}

function renderizarPublicacoes() {
  const posts = publicacoesVisiveis();
  elements.postList.replaceChildren();
  elements.feedCount.textContent = String(posts.length);
  elements.emptyFeed.hidden = posts.length > 0;

  posts.forEach((post) => {
    const card = document.createElement("article");
    card.className = "post-card";
    const topline = document.createElement("div");
    topline.className = "post-topline";
    const category = document.createElement("span");
    category.className = `post-category category-${post.categoria}`;
    category.textContent = {
      pedido: "Pedido de ajuda",
      oferta: "Oferta de ajuda",
      troca: "Doação ou troca",
      evento: "Encontro ou mutirão",
      problema: "Problema no bairro",
    }[post.categoria];
    const localOnly = document.createElement("span");
    localOnly.className = "post-local-only";
    localOnly.textContent = "NESTE NAVEGADOR";
    topline.append(category, localOnly);

    const title = document.createElement("h3");
    title.textContent = post.titulo;
    const description = document.createElement("p");
    description.className = "post-description";
    description.textContent = post.descricao;
    const meta = document.createElement("div");
    meta.className = "post-meta";
    meta.textContent = post.bairro
      ? `${post.bairro} · ${state.selectedDistrict.nome} · ${post.hora} · local`
      : `${state.selectedDistrict.nome} · ${post.hora} · local`;
    const removeButton = document.createElement("button");
    removeButton.className = "post-remove";
    removeButton.type = "button";
    removeButton.textContent = "Excluir deste navegador";
    removeButton.addEventListener("click", () => excluirPublicacao(post.id));
    card.append(topline, title, description, meta, removeButton);
    elements.postList.append(card);
  });
}

function excluirPublicacao(id) {
  const publicacoes = state.posts.filter((post) => post.id !== id);
  try {
    window.localStorage.setItem(
      communityStorageKey,
      JSON.stringify(publicacoes),
    );
  } catch (erro) {
    elements.communityStorage.textContent =
      "Não foi possível atualizar o armazenamento local. A publicação continua salva neste navegador.";
    return;
  }
  state.posts = publicacoes;
  renderizarPublicacoes();
  elements.communityStorage.textContent =
    "Publicação excluída deste navegador. Nenhuma outra pessoa recebeu ou verá essa alteração.";
}

function adicionarPublicacao(evento) {
  evento.preventDefault();
  elements.postError.hidden = true;
  if (!state.selectedDistrict) {
    elements.postError.textContent = "Escolha seu distrito antes de publicar.";
    elements.postError.hidden = false;
    return;
  }
  if (state.posts.length >= 100) {
    elements.postError.textContent =
      "Este navegador atingiu o limite de 100 exemplos locais.";
    elements.postError.hidden = false;
    return;
  }

  const bairro = elements.postNeighborhood.value.trim().replace(/\s+/g, " ");
  const post = {
    id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    categoria: elements.postCategory.value,
    codigoCidade: 3550308,
    codigoDistrito: state.selectedDistrict.codigo_ibge,
    bairro,
    titulo: elements.postTitle.value.trim(),
    descricao: elements.postDescription.value.trim(),
    criadoEm: new Date().toISOString(),
    hora: new Intl.DateTimeFormat("pt-BR", {
      hour: "2-digit",
      minute: "2-digit",
    }).format(new Date()),
  };
  if (!post.titulo || !post.descricao) {
    elements.postError.textContent = "Preencha o título e a descrição.";
    elements.postError.hidden = false;
    return;
  }

  const publicacoes = [post, ...state.posts];
  try {
    window.localStorage.setItem(
      communityStorageKey,
      JSON.stringify(publicacoes),
    );
  } catch (erro) {
    elements.postError.textContent =
      "Não foi possível salvar neste navegador. Verifique o espaço disponível ou as permissões e tente novamente.";
    elements.postError.hidden = false;
    return;
  }

  state.posts = publicacoes;
  elements.postForm.reset();
  elements.postCategory.value = "pedido";
  elements.postNeighborhood.value = state.selectedNeighborhood;
  elements.communityStorage.textContent =
    "Exemplo salvo neste navegador. Ele não foi enviado nem compartilhado com outros moradores.";
  renderizarPublicacoes();
}

function carregarPublicacoesSalvas() {
  try {
    const conteudo = window.localStorage.getItem(communityStorageKey);
    if (!conteudo) {
      return;
    }
    const publicacoes = JSON.parse(conteudo);
    if (
      !Array.isArray(publicacoes) ||
      !publicacoes.every(
        (post) =>
          post &&
          ["pedido", "oferta", "troca", "evento", "problema"].includes(
            post.categoria,
          ) &&
          typeof post.id === "string" &&
          Number.isInteger(post.codigoDistrito) &&
          post.codigoCidade === 3550308 &&
          typeof post.bairro === "string" &&
          typeof post.titulo === "string" &&
          typeof post.descricao === "string" &&
          typeof post.hora === "string",
      )
    ) {
      throw new Error("Os exemplos locais salvos têm formato inválido.");
    }
    state.posts = publicacoes.slice(0, 100);
  } catch (erro) {
    elements.communityStorage.textContent =
      "Não foi possível carregar os exemplos salvos neste navegador. Você ainda pode explorar o mural sem publicar.";
  }
}

const secoesDeNavegacao = Array.from(document.querySelectorAll(".main-nav a"))
  .map((link) => ({
    link,
    secao: document.querySelector(link.getAttribute("href")),
  }))
  .filter((item) => item.secao);

if ("IntersectionObserver" in window) {
  const observadorDeSecoes = new IntersectionObserver(
    (entradas) => {
      const visiveis = entradas
        .filter((entrada) => entrada.isIntersecting)
        .sort((a, b) => b.intersectionRatio - a.intersectionRatio);
      if (visiveis.length === 0) {
        return;
      }
      secoesDeNavegacao.forEach(({ link, secao }) => {
        const ativa = secao === visiveis[0].target;
        link.classList.toggle("is-current", ativa);
        if (ativa) {
          link.setAttribute("aria-current", "location");
        } else {
          link.removeAttribute("aria-current");
        }
      });
    },
    { rootMargin: "-25% 0px -60% 0px", threshold: [0, 0.25, 0.5, 0.75] },
  );
  secoesDeNavegacao.forEach(({ secao }) => observadorDeSecoes.observe(secao));
}

document.querySelectorAll(".metric-button").forEach((botao) => {
  botao.addEventListener("click", () => selecionarIndicador(botao));
});
elements.form.addEventListener("submit", avaliarSimulacao);
elements.territoryForm.addEventListener("submit", aplicarTerritorio);
elements.changeRegion.addEventListener("click", () => {
  document.getElementById("territorio").scrollIntoView({
    behavior: "smooth",
    block: "start",
  });
  elements.districtSelect.focus({ preventScroll: true });
});
elements.postForm.addEventListener("submit", adicionarPublicacao);
elements.postFilter.addEventListener("change", renderizarPublicacoes);
document.querySelectorAll(".community-action").forEach((botao) => {
  botao.addEventListener("click", () => {
    if (!state.selectedDistrict) {
      document.getElementById("territorio").scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
      elements.districtSelect.focus({ preventScroll: true });
      elements.territoryError.textContent =
        "Escolha seu distrito antes de iniciar uma publicação.";
      elements.territoryError.hidden = false;
      return;
    }
    elements.postCategory.value = botao.dataset.postCategory;
    elements.postForm.scrollIntoView({ behavior: "smooth", block: "center" });
    elements.postTitle.focus({ preventScroll: true });
  });
});
elements.retryServices.addEventListener("click", () => {
  if (state.selectedDistrict) {
    carregarServicos(state.selectedDistrict);
  }
});
carregarPublicacoesSalvas();
renderizarPublicacoes();
carregarDistritos();
carregarClima();

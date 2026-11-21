/* AVIVA | Interface de Reabilitação: pesquisa de serviços, mapa e filtros geográficos. */
(function () {
  'use strict';
  const $ = (id) => document.getElementById(id);
  const form = $('searchForm');
  const feedback = $('searchFeedback');
  const results = $('results');
  const zona = $('zona');
  const bairro = $('bairro');
  const categoria = $('categoria');
  const pagination = $('pagination');
  const previousButton = $('prevPage');
  const nextButton = $('nextPage');
  const pageStatus = $('pageStatus');
  const mapPanel = $('mapPanel');
  const mapStatus = $('mapStatus');
  const listPanel = $('listPanel');
  const nearestPanel = $('nearestPanel');
  const nearestResults = $('nearestResults');
  const locationMessage = $('locationMessage');
  let currentPage = 1;
  let numberOfPages = 1;
  let latestAreaRequest = 0;
  let latestSearchRequest = 0;
  let currentView = 'both';
  let map = null;
  let fallbackMap = false;
  let markers = null;
  let userMarker = null;
  let selectedOrigin = null;
  let selectingPoint = false;
  let visibleMapPoints = [];
  let mappedTotal = 0;
  let unmappedTotal = 0;

  function atualizarAvisoUBS() {
    $('ubsSearchNotice').hidden = categoria.value !== 'UBS';
  }

  function el(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }
  function safeSource(item) {
    return typeof item.fonte_url === 'string' && item.fonte_url.startsWith('https://') ? item.fonte_url : null;
  }
  function addSourceLink(container, item, label='Fonte CNES ↗') {
    const url = safeSource(item);
    if (!url) return;
    const a = el('a', '', label);
    a.href = url;
    a.rel = 'noopener noreferrer';
    a.target = '_blank';
    container.append(a);
  }
  function message(title, detail) {
    pagination.hidden = true;
    feedback.hidden = false;
    feedback.replaceChildren(el('div', 'empty-icon', '⌕'), el('strong', '', title), el('p', '', detail));
    results.replaceChildren();
  }
  function listServices(items, total, page, limit) {
    results.replaceChildren();
    const first = (page - 1) * limit + 1;
    const last = Math.min(page * limit, total);
    results.append(el('p', 'disclaimer', `${total} registros encontrados. Exibindo ${first}–${last}. Serviços documentados estão identificados; disponibilidade de atendimento ainda requer confirmação.`));
    for (const item of items) {
      const card = el('article', 'result-card');
      card.append(el('h3', '', item.nome), el('p', '', `${item.municipio} · ${item.uf}`));
      if (item.endereco) card.append(el('p', '', item.endereco + (item.bairro ? ' · ' + item.bairro : '')));
      if (item.telefone) card.append(el('p', '', `Telefone cadastrado: ${item.telefone}`));
      const tags = el('div');
      tags.append(el('span', 'result-tag', item.tipo_fonte==='institucional_documentado' ? 'Oficina documentada · fonte institucional' : item.tipo_fonte==='cnes_tipo_unidade_ubs' ? 'UBS · tipo 2 + nome no CNES' : `${item.categoria_indicio_nome} (indício pelo nome)`));
      if (item.zona_preliminar) {
        const nomes = {norte:'Zona Norte',sul:'Zona Sul',leste:'Zona Leste',oeste:'Zona Oeste',centro:'Centro',nao_identificada:'Zona não identificada'};
        tags.append(el('span', 'result-tag', `Zona preliminar: ${nomes[item.zona_preliminar] || 'Não identificada'}`));
      }
      tags.append(el('span', 'result-tag', `Ambulatorial SUS informado: ${item.ambulatorial_sus_informado}`));
      const locTxt={
        ponto_correspondente_referencia_externa:'UBS: localização conferida com Prefeitura e CNES (endereço compatível)',
        divergencia_endereco_entre_fontes:'ATENÇÃO: Prefeitura e CNES divergem no endereço; pin não validado',
        ponto_fora_area_referencia_pendente:'ATENÇÃO: ponto municipal fora da área da própria UBS; revisar',
        pendente_validacao_em_fonte_externa:'Localização ainda não conferida em fonte independente',
        suspeita_automatica_sem_referencia_externa:'ALERTA: coordenada suspeita; pin ocultado',
        sem_coordenadas_confiaveis:'Sem coordenadas aproveitáveis'
      }[item.status_localizacao] || 'Localização não verificada';
      tags.append(el('span','result-tag',locTxt));
      card.append(tags, el('p', '', `CNES: ${item.cnes} · ${item.tipo_fonte==='institucional_documentado' ? 'Oficina documentada; atendimento a confirmar' : item.tipo_fonte==='cnes_tipo_unidade_ubs' ? 'UBS cadastrada; serviços e acesso a confirmar' : 'Verificação pendente'}`));
      if (item.acesso) card.append(el('p','', 'Como acessar: ' + item.acesso));
      addSourceLink(card, item, item.tipo_fonte==='institucional_documentado' ? 'Ver fonte institucional ↗' : 'Conhecer a fonte CNES ↗');
      if (item.endereco) {
        const geoSearch=el('a','','Conferir endereço no OpenStreetMap ↗');
        geoSearch.href='https://www.openstreetmap.org/search?query='+encodeURIComponent([item.endereco,item.bairro,item.municipio,'Brasil'].filter(Boolean).join(', '));
        geoSearch.target='_blank'; geoSearch.rel='noopener noreferrer';
        card.append(geoSearch);
      }
      card.append(el('p', 'disclaimer', item.aviso));
      results.append(card);
    }
  }
  async function atualizarBairros() {
    const seq = ++latestAreaRequest;
    const previouslySelected = bairro.value;
    bairro.disabled = true;
    const params = new URLSearchParams();
    if (zona.value) params.set('zona', zona.value);
    if (categoria.value) params.set('categoria', categoria.value);
    try {
      const response = await fetch('/api/v1/reabilitacao/cnes/bairros-sp?' + params.toString());
      if (!response.ok) throw new Error('Erro ao carregar bairros');
      const data = await response.json();
      if (seq !== latestAreaRequest) return;
      bairro.replaceChildren(new Option('Todos os bairros', ''));
      for (const value of data.bairros) bairro.add(new Option(value, value));
      if (data.bairros.includes(previouslySelected)) bairro.value = previouslySelected;
      bairro.disabled = false;
    } catch (_) {
      if (seq !== latestAreaRequest) return;
      bairro.replaceChildren(new Option('Bairros indisponíveis', ''));
      bairro.disabled = true;
    }
  }
  function mapParams(expandLocation=false) {
    const params = new URLSearchParams();
    params.set('modo', expandLocation ? 'validado' : 'todos');
    if (categoria.value) params.set('categoria', categoria.value);
    if (!expandLocation) {
      if (zona.value) params.set('zona', zona.value);
      if (bairro.value) params.set('bairro', bairro.value);
    }
    return params;
  }
  function drawFallback(items) {
    
    
    const node = $('map');
    node.replaceChildren();
    node.classList.add('offline-map');
    const svgns = 'http://www.w3.org/2000/svg';
    const svgEl = (tag, attrs={}) => {
      const e=document.createElementNS(svgns,tag);
      Object.entries(attrs).forEach(([k,v])=>e.setAttribute(k,v));
      return e;
    };
    const svg=svgEl('svg',{viewBox:'0 0 900 440','aria-label':'Prévia geográfica dos pins, sem ruas'});
    const coords=items.map(i=>[i.latitude,i.longitude]);
    if (selectedOrigin) coords.push([selectedOrigin.lat,selectedOrigin.lon]);
    let latMin=-23.85,latMax=-23.35,lonMin=-46.90,lonMax=-46.35;
    if (coords.length) {
      latMin=Math.min(...coords.map(p=>p[0]), latMin);
      latMax=Math.max(...coords.map(p=>p[0]),latMax);
      lonMin=Math.min(...coords.map(p=>p[1]), lonMin);
      lonMax=Math.max(...coords.map(p=>p[1]),lonMax);
    }
    const x=(lon)=>30+(lon-lonMin)/(lonMax-lonMin)*840;
    const y=(lat)=>30+(latMax-lat)/(latMax-latMin)*380;
    const rect=svgEl('rect',{x:0,y:0,width:900,height:440,fill:'#eaf4ee'});
    svg.append(rect);
    for (let i=0;i<=10;i++) {
      svg.append(svgEl('line',{x1:30+i*84,y1:0,x2:30+i*84,y2:440,stroke:'#d3e4da','stroke-width':1}));
      svg.append(svgEl('line',{x1:0,y1:30+i*38,x2:900,y2:30+i*38,stroke:'#d3e4da','stroke-width':1}));
    }
    const label=svgEl('text',{x:22,y:28,fill:'#285d55','font-size':16,'font-weight':'bold'});
    label.textContent='SÃO PAULO · Prévia de coordenadas, sem ruas'; svg.append(label);
    for (const item of items) {
      const dot=svgEl('circle',{cx:x(item.longitude),cy:y(item.latitude),r:item.distanceKm!==undefined?8:5.5,fill:!item.pin_validado?'#f39b4a':item.distanceKm!==undefined?'#e58d36':item.tipo_fonte==='cnes_tipo_unidade_ubs'?'#3678bd':'#0b948a',stroke:item.pin_validado?'#fff':'#703e15','stroke-width':item.pin_validado?1.5:2});
      const title=svgEl('title');
      title.textContent=`${item.nome} — ${item.bairro}. ${item.pin_validado?'Posição conferida em fonte municipal.':'POSIÇÃO NÃO CONFIRMADA.'} ${item.aviso_validacao || 'Atendimento a confirmar.'}`;
      dot.append(title);
      dot.addEventListener('click', (event) => {event.stopPropagation();locationMessage.textContent = `${item.nome}: ${item.aviso_validacao || 'Endereço e atendimento a confirmar.'}`;});
      svg.append(dot);
    }
    if (selectedOrigin) svg.append(svgEl('circle',{cx:x(selectedOrigin.lon),cy:y(selectedOrigin.lat),r:11,fill:'#facd78',stroke:'#92591d','stroke-width':3}));
    svg.addEventListener('click',(event)=>{
      if(!selectingPoint)return;
      const r=svg.getBoundingClientRect();
      const px=(event.clientX-r.left)/r.width*900;
      const py=(event.clientY-r.top)/r.height*440;
      const lon=lonMin+(px-30)/840*(lonMax-lonMin);
      const lat=latMax-(py-30)/380*(latMax-latMin);
      selectingPoint=false;
      setOrigin(lat,lon,'Ponto marcado manualmente');
    });
    node.append(svg);
  }
  function ensureMap() {
    if (map || fallbackMap) return true;
    if (!window.L) {
      fallbackMap=true;
      drawFallback(visibleMapPoints);
      mapStatus.textContent = 'Mapa-base indisponível; mostrando prévia geográfica sem ruas. Conecte-se à internet para visualizar o OpenStreetMap.';
      return true;
    }
    map = window.L.map('map', {scrollWheelZoom:false, preferCanvas:true}).setView([-23.5505, -46.6333], 11);
    window.L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">OpenStreetMap contributors</a>'
    }).addTo(map);
    markers = window.L.layerGroup().addTo(map);
    map.on('click', (event) => {
      if (!selectingPoint) return;
      selectingPoint = false;
      setOrigin(event.latlng.lat, event.latlng.lng, 'Ponto marcado manualmente');
      locationMessage.textContent = 'Ponto marcado. Clique em “Encontrar 5 mais próximos” para pesquisar em toda São Paulo.';
    });
    renderMapPoints(visibleMapPoints, false);
    return true;
  }
  function popupContent(item) {
    const popup = el('div', 'map-popup');
    popup.append(el('strong', '', item.nome));
    popup.append(el('span', item.pin_validado ? 'map-valid-status' : 'map-pending-status', item.pin_validado ? 'Endereço cruzado com Prefeitura (2026)' : 'Atenção · localização não confirmada'));
    popup.append(el('p', '', [item.endereco, item.bairro].filter(Boolean).join(' · ')));
    popup.append(el('p', item.pin_validado ? 'map-verified-note' : 'map-warning-note', item.aviso_validacao || 'Verifique o endereço e a situação do estabelecimento antes de ir.'));
    popup.append(el('p', '', `${item.tipo_fonte==='institucional_documentado' ? 'Oficina documentada' : item.tipo_fonte==='cnes_tipo_unidade_ubs' ? 'UBS cadastrada no CNES (tipo 2)' : 'Categoria por nome: '+item.categoria_indicio_nome} · CNES ${item.cnes}`));
    if (item.observacao_localizacao && !item.pin_validado) popup.append(el('p','',item.observacao_localizacao));
    if (item.fonte_coordenada) { const a=el('a','', 'Fonte da coordenada revisada ↗'); a.href=item.fonte_coordenada; a.target='_blank'; a.rel='noopener noreferrer'; popup.append(a); }
    if (item.descricao_fonte_coordenada) popup.append(el('p','map-data-origin', `Coordenada: ${item.descricao_fonte_coordenada}`));
    if (item.distanceKm !== undefined) popup.append(el('p', '', `${item.distanceKm.toFixed(2).replace('.', ',')} km em linha reta do ponto indicado`));
    addSourceLink(popup, item);
    if (item.endereco) {const a=el('a','', 'Pesquisar endereço no mapa ↗');a.href='https://www.openstreetmap.org/search?query='+encodeURIComponent([item.endereco,item.bairro,'São Paulo','Brasil'].filter(Boolean).join(', '));a.rel='noopener noreferrer';a.target='_blank';popup.append(a);}
    popup.append(el('em', '', item.tipo_fonte==='institucional_documentado' ? 'Oficina documentada; disponibilidade e condições de atendimento pelo SUS não confirmadas.' : item.tipo_fonte==='cnes_tipo_unidade_ubs' ? 'UBS cadastrada. Oferta de reabilitação, vagas e UBS de referência não confirmadas.' : 'Cadastro candidato: habilitação, modalidade e atendimento ainda não verificados.'));
    return popup;
  }
  function hoverContent(item) {
    
    const tip = el('div', 'aviva-pin-hover');
    tip.append(el('strong', '', item.nome));
    tip.append(el('span', '', [item.endereco, item.bairro].filter(Boolean).join(' · ')));
    tip.append(el('b', item.pin_validado ? 'tip-verified' : 'tip-warning',
      item.pin_validado ? 'Localização conferida · atendimento a confirmar' : '⚠ Endereço/localização ou existência não confirmados'));
    if (!item.pin_validado) tip.append(el('span', '', item.aviso_validacao));
    return tip;
  }
  function renderMapPoints(items, shouldFit=true) {
    visibleMapPoints = items;
    if (fallbackMap) {drawFallback(items);return;}
    if (!map || !markers) return;
    markers.clearLayers();
    const bounds = [];
    const leaf = window.L;
    for (const item of items) {
      const latlng = [item.latitude, item.longitude];
      bounds.push(latlng);
      const nearest = item.distanceKm !== undefined;
      const marker = leaf.circleMarker(latlng, {
        radius: nearest ? 9 : 7,
        color: item.pin_validado ? (nearest ? '#aa5c20' : '#fff') : '#874b1d',
        weight: item.pin_validado ? (nearest?2:1.5) : 2,
        dashArray: item.pin_validado ? null : '3 3',
        fillColor: !item.pin_validado ? '#f39b4a' : nearest ? '#e58d36' : item.tipo_fonte==='cnes_tipo_unidade_ubs' ? '#3678bd' : '#0b948a',
        fillOpacity: .92
      });
      marker.bindTooltip(hoverContent(item), {sticky:true, direction:'top', opacity:1, className:'aviva-tooltip'});
      marker.bindPopup(popupContent(item)); 
      markers.addLayer(marker);
    }
    if (shouldFit && bounds.length) {
      if (selectedOrigin && items.some(i=>i.distanceKm!==undefined)) bounds.push([selectedOrigin.lat, selectedOrigin.lon]);
      map.fitBounds(leaf.latLngBounds(bounds).pad(.12), {maxZoom:14});
    } else if (shouldFit && !items.length) {
      map.setView([-23.5505,-46.6333], 11);
    }
  }
  function updateMapStatus(payload) {
    const confirmed = payload.total_pins_validados || 0;
    const uncertain = payload.total_pins_exploratorios || 0;
    const notMapped = payload.total_sem_coordenadas || 0;
    mapStatus.textContent = `${confirmed} ponto(s) conferido(s) · ${uncertain} ponto(s) exploratório(s) com aviso · ${notMapped} registro(s) sem coordenadas aproveitáveis (na lista). Pins não garantem serviço ativo, horário ou vaga.${fallbackMap?' Mapa-base indisponível.':''}`;
  }
  function changeView(view) {
    if (!['list','map','both'].includes(view)) return;
    currentView = view;
    listPanel.hidden = view === 'map';
    mapPanel.hidden = view === 'list';
    document.querySelectorAll('[data-view]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.view===view)));
    if (view !== 'list' && ensureMap()) {
      setTimeout(() => { if(map)map.invalidateSize(); renderMapPoints(visibleMapPoints, false); }, 90);
    }
  }
  async function atualizarMapa(seq) {
    try {
      const response = await fetch('/api/v1/reabilitacao/cnes/mapa-sp?' + mapParams().toString());
      if (!response.ok) throw new Error('O serviço de mapa não respondeu');
      const payload = await response.json();
      if (seq !== latestSearchRequest) return;
      mappedTotal = payload.total_com_coordenadas;
      unmappedTotal = payload.total_sem_coordenadas;
      renderMapPoints(payload.pontos);
      updateMapStatus(payload);
      if (!mappedTotal && payload.total_candidatos_filtro) {
        locationMessage.textContent = 'Há registros com endereço cadastrado, mas sem coordenadas aproveitáveis para o mapa. Veja os detalhes na lista e confirme com a unidade.';
      }
    } catch (_) {
      if (seq !== latestSearchRequest) return;
      mapStatus.textContent = 'Não foi possível obter os pins agora. A lista pode continuar disponível.';
    }
  }
  async function pesquisar(page=1) {
    const seq = ++latestSearchRequest;
    currentPage = page;
    nearestPanel.hidden = true;
    const params = new URLSearchParams();
    for (const [key, value] of new FormData(form).entries()) if (String(value).trim()) params.set(key, String(value).trim());
    params.set('pagina', String(page));
    params.set('limite', '30');
    $('searchActions').hidden = true;
    message('Consultando registros CNES...', 'Pesquisa exploratória; confirme modalidades e disponibilidade antes de ir.');
    try {
      const response = await fetch('/api/v1/reabilitacao/cnes/candidatos?' + params.toString());
      const payload = await response.json();
      if (seq !== latestSearchRequest) return;
      if (!response.ok) {
        message('Confira os filtros', payload.detail || 'Não foi possível validar os filtros.');
        return;
      }
      if (!payload.total) {
        message('Nenhum registro encontrado neste bairro ou filtro', 'Isso não significa ausência de atendimento. Use “Buscar também em outros bairros” ou marque sua casa para encontrar os mais próximos.');
        $('searchActions').hidden = !Boolean(zona.value || bairro.value);
      } else {
        feedback.hidden = true;
        listServices(payload.resultados, payload.total, page, payload.limite);
        numberOfPages = Math.ceil(payload.total / payload.limite);
        pageStatus.textContent = `Página ${page} de ${numberOfPages}`;
        previousButton.disabled = page <= 1;
        nextButton.disabled = page >= numberOfPages;
        pagination.hidden = numberOfPages <= 1;
      }
      
      if (page===1) await atualizarMapa(seq);
    } catch (_) {
      if (seq !== latestSearchRequest) return;
      message('API não disponível', 'Abra pelo servidor Python, não pelo arquivo HTML.');
      mapStatus.textContent = 'Sem conexão com a API de dados.';
    }
  }
  function setOrigin(lat, lon, label) {
    if (!Number.isFinite(lat) || !Number.isFinite(lon)) return;
    selectedOrigin = {lat,lon,label};
    $('clearOrigin').hidden = false;
    if (ensureMap() && map) {
      if (userMarker) map.removeLayer(userMarker);
      userMarker = window.L.circleMarker([lat,lon], {radius:10,color:'#92591d',weight:3,fillColor:'#facd78',fillOpacity:1}).addTo(map);
      userMarker.bindPopup('Ponto de partida indicado por você — não armazenado').openPopup();
      map.setView([lat,lon], Math.max(12, map.getZoom()));
    } else if (fallbackMap) {
      drawFallback(visibleMapPoints);
    }
    $('originLabel').textContent = `· ${label}`;
    locationMessage.textContent = `${label} selecionado. Sua posição é usada apenas nesta página para calcular distâncias em linha reta.`;
  }
  function haversineKm(a,b,c,d) {
    const R=6371.0088;
    const rad=Math.PI/180;
    const dLat=(c-a)*rad;
    const dLon=(d-b)*rad;
    const h=Math.sin(dLat/2)**2 + Math.cos(a*rad)*Math.cos(c*rad)*Math.sin(dLon/2)**2;
    return 2*R*Math.asin(Math.min(1,Math.sqrt(h)));
  }
  async function findNearest() {
    if (!selectedOrigin) {
      locationMessage.textContent = 'Primeiro clique em “Usar minha localização” ou “Marcar minha casa no mapa”.';
      return;
    }
    const button = $('findNearest');
    button.disabled = true;
    locationMessage.textContent = 'Calculando os serviços mais próximos (em linha reta)…';
    try {
      
      const response = await fetch('/api/v1/reabilitacao/cnes/mapa-sp?' + mapParams(true).toString());
      if (!response.ok) throw new Error('Erro na consulta');
      const payload = await response.json();
      const nearest = payload.pontos.map(p=>({
        ...p, distanceKm:haversineKm(selectedOrigin.lat, selectedOrigin.lon,p.latitude,p.longitude)
      })).sort((a,b)=>a.distanceKm-b.distanceKm).slice(0,5);
      nearestPanel.hidden = false;
      nearestResults.replaceChildren();
      if (!nearest.length) {
        nearestResults.append(el('p', '', 'Não há posições conferidas desta categoria para calcular os mais próximos. Confira os pins exploratórios, com seus avisos, e confirme o endereço antes de se deslocar.'));
      }
      nearest.forEach((item,index) => {
        const card = el('article','nearest-card');
        const info=el('div');
        info.append(el('h4','',`${index+1}. ${item.nome}`));
        info.append(el('p','',[item.endereco,item.bairro].filter(Boolean).join(' · ')));
        info.append(el('p','',`${item.categoria_indicio_nome} · CNES ${item.cnes} · ${item.tipo_fonte==='institucional_documentado' ? 'Oficina documentada; atendimento a confirmar' : item.tipo_fonte==='cnes_tipo_unidade_ubs' ? 'UBS cadastrada; serviços a confirmar' : 'Situação não verificada'}`));
        if (item.aviso_validacao) info.append(el('p','',item.aviso_validacao));
        addSourceLink(info,item);
        card.append(info,el('span','distance-badge',`${item.distanceKm.toFixed(2).replace('.',',')} km`));
        nearestResults.append(card);
      });
      if (nearest.length) {
        changeView('map');
        renderMapPoints(nearest);
        mapStatus.textContent = `Exibindo ${nearest.length} ponto(s) com endereço cruzado com a Prefeitura. Distâncias em linha reta, não rotas. Use a pesquisa para voltar a ver todos os pins.`;
        locationMessage.textContent = 'Busca concluída usando apenas pontos cruzados com fonte cartográfica independente. Confirme funcionamento e entrada antes de sair de casa.';
      }
    } catch (_) {
      locationMessage.textContent = 'Não foi possível calcular a proximidade. Confira se o servidor AVIVA está funcionando.';
    } finally {button.disabled=false;}
  }
  function useCurrentLocation() {
    if (!navigator.geolocation) {
      locationMessage.textContent = 'Geolocalização não disponível neste navegador. Use “Marcar minha casa no mapa”.';
      return;
    }
    locationMessage.textContent = 'Aguardando sua autorização de localização no navegador…';
    navigator.geolocation.getCurrentPosition(
      position=>{ setOrigin(position.coords.latitude,position.coords.longitude,'Localização autorizada'); changeView('map'); },
      error=>{ locationMessage.textContent = `Não foi possível obter sua localização (${error.code===1?'permissão recusada':'sinal indisponível ou tempo esgotado'}). Marque o ponto manualmente no mapa.`; },
      {enableHighAccuracy:false,timeout:12000,maximumAge:0}
    );
  }
  form.addEventListener('submit',event=>{event.preventDefault();changeView('both');pesquisar(1);});
  zona.addEventListener('change',atualizarBairros);
  categoria.addEventListener('change',()=>{atualizarAvisoUBS();atualizarBairros();});
  previousButton.addEventListener('click',()=>pesquisar(currentPage-1));
  nextButton.addEventListener('click',()=>pesquisar(currentPage+1));
  document.querySelectorAll('[data-view]').forEach(b=>b.addEventListener('click',()=>changeView(b.dataset.view)));
  $('useCurrentLocation').addEventListener('click',useCurrentLocation);
  $('pickOnMap').addEventListener('click',()=>{
    changeView('map');
    selectingPoint=true;
    locationMessage.textContent='Clique no mapa para marcar o ponto de sua casa (ou outro ponto de partida). Não é necessário informar endereço.';
  });
  $('findNearest').addEventListener('click',findNearest);
  $('clearOrigin').addEventListener('click',()=>{
    selectedOrigin=null; selectingPoint=false; nearestPanel.hidden=true;
    $('clearOrigin').hidden=true;
    if (userMarker && map) map.removeLayer(userMarker);
    userMarker=null;
    if (fallbackMap) drawFallback(visibleMapPoints);
    locationMessage.textContent='Ponto removido. Você poderá escolher outro quando quiser.';
    pesquisar(1);
  });
  $('expandSearch').addEventListener('click',async()=>{
    zona.value='';bairro.value='';await atualizarBairros();pesquisar(1);
  });
  document.querySelectorAll('.nav-link').forEach(link=>link.addEventListener('click',()=>{
    document.querySelectorAll('.nav-link').forEach(l=>l.classList.remove('current'));
    link.classList.add('current');
  }));
  changeView('both');
  atualizarAvisoUBS();
  atualizarBairros().then(()=>pesquisar(1));
})();

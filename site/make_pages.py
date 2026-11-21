"""AVIVA | Geração das páginas institucionais estáticas.
Reúne a estrutura visual, os componentes e a navegação do portal.
"""
from pathlib import Path
import html
ROOT=Path(__file__).resolve().parent

icons={
 'health':'<path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1.1-1.1a5.5 5.5 0 0 0-7.8 7.8L12 21l8.8-8.6a5.5 5.5 0 0 0 0-7.8Z"/><path d="M3.5 12h4l2-3 3 6 2-3h6"/>',
 'people':'<path d="M16 20v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 20v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>',
 'cloud':'<path d="M18 10a4 4 0 0 0-4-4 5 5 0 0 0-9.7 1.6A4.5 4.5 0 0 0 6 16.5h12a3.25 3.25 0 0 0 0-6.5Z"/><path d="M20 2v2M21 6h2M17 3l1-1"/>',
 'map':'<path d="M20 10c0 5-8 12-8 12S4 15 4 10a8 8 0 1 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
 'arrow':'<path d="M5 12h14m-6-6 6 6-6 6"/>',
 'check':'<path d="m4 12 5 5L20 6"/>',
 'book':'<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2Z"/>',
 'shield':'<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z"/><path d="m9 12 2 2 4-4"/>',
 'search':'<circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/>',
 'info':'<circle cx="12" cy="12" r="10"/><path d="M12 16v-4m0-4h.01"/>',
 'users':'<path d="M16 21v-2a4 4 0 0 0-4-4H7a4 4 0 0 0-4 4v2"/><circle cx="9.5" cy="7" r="4"/><path d="M17 11a4 4 0 1 0-1-7.9M21 21v-2a4 4 0 0 0-3-3.9"/>',
 'sun':'<circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M4.9 4.9l1.4 1.4m11.4 11.4 1.4 1.4M2 12h2m16 0h2M4.9 19.1l1.4-1.4m11.4-11.4 1.4-1.4"/>',
 'heart-hand':'<path d="M6 10 12 4l6 6M4 14h16M4 18h16"/>',
 'help':'<circle cx="12" cy="12" r="10"/><path d="M9.5 9a3 3 0 0 1 5.9.7c0 2-3.4 2.5-3.4 4.6M12 17h.01"/>',
 'house':'<path d="m3 10 9-7 9 7v10H3V10Z"/><path d="M9 20v-7h6v7"/>',
 'lock':'<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>',
 'menu':'<path d="M4 6h16M4 12h16M4 18h16"/>',
 'close':'<path d="M6 6l12 12M18 6 6 18"/>',
 'wheel':'<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="2"/><path d="m12 10-4-5m4 9 5 5"/>',
 'mail':'<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m2 6 10 7 10-7"/>'
}
def icon(name,css=''):
 return f'<svg class="icon {css}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{icons[name]}</svg>'

def card(iconname,eyebrow,title,desc,href,chip=None):
 return f'''<a class="service-card" href="{href}">
 <span class="card-icon">{icon(iconname)}</span>
 <span class="card-label">{eyebrow}</span><strong>{title}</strong>
 <span class="card-description">{desc}</span>
 <span class="card-bottom">{f'<span class="chip">{chip}</span>' if chip else ''}<span class="card-arrow">{icon('arrow')}</span></span>
 </a>'''

def base(title, active, body, description):
 nav=lambda t, path: f'<a href="{path}" class="nav-item {"active" if t == active else ""}" {"aria-current=page" if t == active else ""}>{t}</a>'
 return f'''<!DOCTYPE html><html lang="pt-BR"><head>
 <meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="theme-color" content="#ffffff">
 <title>{title} | AVIVA</title><meta name="description" content="{description}">
 <meta name="color-scheme" content="light"><link rel="icon" type="image/png" href="/assets/icon-192.png">
 <link rel="manifest" href="/manifest.webmanifest">
 <link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
 <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap" rel="stylesheet">
 <link rel="stylesheet" href="/assets/site.css"><script defer src="/assets/site.js"></script>
 </head><body data-page="{active}"><a class="skip" href="#main">Ir ao conteúdo</a>
 <header class="header"><div class="header-inner wrap">
 <a class="logo-link" href="/" aria-label="AVIVA — página inicial"><img src="/assets/aviva-symbol.png" class="logo-symbol" alt=""><strong>AVIVA</strong></a>
 <nav class="nav-desktop" aria-label="Navegação principal">{nav('Início','/')}{nav('Auxílios','/auxilios/')}{nav('Sobre','/sobre/')}</nav>
 <div class="header-right"><a class="login-button {"login-current" if active=='Login' else ''}" href="/login/">{icon('lock')}<span>Login</span></a>
 <button class="menu-toggle" type="button" aria-label="Abrir menu" aria-controls="mobile-nav" aria-expanded="false">{icon('menu')}</button></div>
 </div><nav id="mobile-nav" class="mobile-nav" aria-label="Menu mobile" hidden>{nav('Início','/')}{nav('Auxílios','/auxilios/')}{nav('Sobre','/sobre/')}<a href="/login/">Login</a></nav></header>
 <main id="main">{body}</main>
 <footer class="footer"><div class="wrap footer-body"><div><a class="footer-logo" href="/">{icon('people')}<strong>AVIVA</strong></a><p>Comunidade, saúde e informação mais perto de você.</p></div><nav aria-label="Links do rodapé"><a href="/">Início</a><a href="/auxilios/">Auxílios</a><a href="/sobre/">Sobre</a><a href="/login/">Login</a></nav></div>
 <div class="wrap footer-foot"><span>Protótipo acadêmico CitizenTech · 2026</span><span>O AVIVA orienta; não substitui profissionais ou serviços públicos.</span></div></footer>
 </body></html>'''

home = f'''
 <section class="hero wrap" aria-labelledby="hero-title">
 <span class="eyebrow"><span class="eyebrow-dot"></span> Tecnologia com propósito social</span>
 <h1 id="hero-title">Comunidade, saúde e<br><span>informação mais perto de você.</span></h1>
 <p class="hero-subtitle">O AVIVA aproxima pessoas de informações úteis, caminhos de cuidado e serviços do território — de forma simples, inclusiva e transparente.</p>
 <div class="hero-actions"><a class="btn btn-orange" href="/auxilios/">Explorar auxílios {icon('arrow')}</a><a class="btn btn-plain" href="/sobre/">Conhecer o AVIVA {icon('arrow')}</a></div>
 <div class="hero-image"><img src="/assets/comunidade-aquarela.webp" alt="Ilustração em aquarela de pessoas de diferentes idades conversando no parque, incluindo um usuário de cadeira de rodas e um homem acompanhado de cão-guia."></div>
 <div class="hero-caption">Juntos, construímos caminhos para uma comunidade mais informada e conectada.</div>
 </section>
 <section class="services wrap" aria-labelledby="services-title">
 <div class="section-heading center"><span class="eyebrow-small">Comece por aqui</span><h2 id="services-title">Como o AVIVA pode ajudar?</h2><p>Escolha o assunto que você precisa. Cada área mostra informações, ferramentas e suas fontes.</p></div>
 <div class="services-grid">
 {card('health','CUIDADO E ORIENTAÇÃO','Saúde e reabilitação','Busque UBS, CAPS e serviços especializados; conheça os caminhos do SUS.','/reabilitacao/','CNES + Prefeitura')}
 {card('people','CONEXÃO LOCAL','Comunidade e território','Explore serviços comunitários, iniciativas e informações do seu distrito.','/comunidade/','São Paulo')}
 {card('cloud','DADOS DO TERRITÓRIO','Clima e riscos','Conheça leituras históricas e demonstrações de análise de situações do território.','/comunidade/#clima','Dados históricos')}
 {card('map','BUSCA DE APOIO','Serviços e auxílios','Encontre por onde começar e descubra os recursos disponíveis no AVIVA.','/auxilios/','Guia de acesso')}
 </div>
 </section>
 <section class="how-section"><div class="wrap"><div class="section-heading center"><span class="eyebrow-small">Sem complicação</span><h2>Informação que ajuda a dar o próximo passo</h2><p>Você não precisa saber o nome técnico de um serviço para começar.</p></div><div class="steps">
 <div class="step"><span class="step-num">01</span>{icon('search')}<h3>Conte o que procura</h3><p>Escolha uma área de ajuda, um serviço ou sua região.</p></div>
 <div class="step"><span class="step-num">02</span>{icon('book')}<h3>Entenda as opções</h3><p>Veja explicações simples, possíveis caminhos e fontes dos dados.</p></div>
 <div class="step"><span class="step-num">03</span>{icon('shield')}<h3>Confira antes de ir</h3><p>Valide endereço, funcionamento e acesso com o serviço responsável.</p></div>
 </div></div></section>
 <section class="wrap trust"><div class="trust-copy"><span class="eyebrow-small">Um compromisso com você</span><h2>Informação clara. <em>Sem promessas que não podemos fazer.</em></h2><p>Usamos dados públicos e identificamos o que ainda precisa de conferência. O AVIVA não faz diagnóstico, não confirma vagas e não substitui os canais oficiais de atendimento.</p><a class="text-link" href="/sobre/">Entenda como funciona {icon('arrow')}</a></div><div class="trust-stat"><span class="check-icon">{icon('check')}</span><strong>Transparência por padrão</strong><p>Serviços e pontos geográficos têm avisos sobre sua origem e nível de verificação.</p><span class="tiny-pill">Protótipo acadêmico · SP</span></div></section>
'''

auxilios = f'''
 <section class="page-hero wrap"><span class="eyebrow"><span class="eyebrow-dot"></span> Auxílios e serviços</span><h1>Encontre o apoio <span>certo para começar.</span></h1><p>Conheça as opções disponíveis no AVIVA. Você pode acessar ferramentas de busca, orientações sobre o SUS e informações da sua região.</p></section>
 <section class="wrap aux-section"><div class="filterbar"><label for="filter-services">Procurar assunto</label><div class="filter-input">{icon('search')}<input id="filter-services" type="search" placeholder="Ex.: CAPS, UBS, clima, bairro, reabilitação" autocomplete="off"></div><span class="filter-note" id="service-count" aria-live="polite">4 áreas para explorar</span></div>
 <div class="services-grid" id="filtered-services">
 {card('health','SAÚDE E REABILITAÇÃO','Encontrar atendimento','Mapa com UBS geograficamente conferidas, orientações sobre CAPS, CER, oficinas e cuidados no SUS.','/reabilitacao/','Serviços SUS')}
 {card('people','CONEXÃO COMUNITÁRIA','Meu território','Selecione seu distrito e explore informações locais, serviços e iniciativas comunitárias.','/comunidade/#territorio','Comunidade')}
 {card('cloud','CLIMA E DADOS','Entender riscos','Explore dados históricos climáticos, cenários e análises experimentais de risco.','/comunidade/#clima','Pesquisa acadêmica')}
 {card('map','LOCALIZAR SERVIÇOS','Serviços do bairro','Consulte pontos de referência comunitários e a presença de equipamentos e serviços.','/comunidade/#recursos','OpenStreetMap')}
 </div><p class="no-results" id="no-results" hidden>Nenhuma área corresponde à sua pesquisa. Experimente outro termo.</p></section>
 <section class="wrap guide-block"><div class="section-heading"><span class="eyebrow-small">Guia simples</span><h2>Entenda os principais serviços de saúde</h2><p>Uma explicação rápida para quem ainda não sabe onde procurar.</p></div><div class="explain-grid">
 <article class="explain"><span>UBS</span><h3>Unidade Básica de Saúde</h3><p>Geralmente é o primeiro local para avaliação, acompanhamento e orientação sobre encaminhamentos.</p></article>
 <article class="explain"><span>CAPS</span><h3>Centro de Atenção Psicossocial</h3><p>Oferece acolhimento e cuidado em saúde mental. É possível procurar diretamente para o primeiro acolhimento.</p></article>
 <article class="explain"><span>CER</span><h3>Centro Especializado em Reabilitação</h3><p>Realiza reabilitação especializada em modalidades habilitadas, com acesso organizado pela rede de saúde.</p></article>
 <article class="explain"><span>ÓRTESES E PRÓTESES</span><h3>Oficinas ortopédicas</h3><p>Podem confeccionar, adaptar e fazer manutenção de recursos assistivos, conforme avaliação e oferta.</p></article>
 </div><a class="btn btn-green" href="/reabilitacao/">Abrir guia de saúde e reabilitação {icon('arrow')}</a></section>
 <section class="wrap information-notice">{icon('info')}<p><strong>Antes de visitar um local:</strong> confirme endereço, atendimento e necessidade de encaminhamento. Cadastros públicos não garantem vagas, horários ou serviços ativos.</p></section>
'''

sobre=f'''
 <section class="page-hero wrap"><span class="eyebrow"><span class="eyebrow-dot"></span> Sobre o AVIVA</span><h1>Informação aproxima. <span>Cuidado transforma.</span></h1><p>O AVIVA é um projeto de tecnologia social pensado para tornar informações e caminhos de acesso mais compreensíveis, começando pela cidade de São Paulo.</p></section>
 <section class="wrap about-layout"><div class="about-illustration"><img src="/assets/comunidade-aquarela.webp" alt="Ilustração em aquarela de uma comunidade diversa convivendo em praça pública."></div><div class="about-text"><span class="eyebrow-small">Por que existimos</span><h2>Um aplicativo para reduzir a distância entre a informação e as pessoas.</h2><p>Reunimos em um mesmo ambiente informações sobre serviços de saúde e reabilitação, comunidade, território e riscos. A proposta é ajudar o cidadão a entender opções, pesquisar serviços e tomar decisões mais informadas.</p><p>O projeto integra dois módulos em desenvolvimento: Comunidade e Saúde & Reabilitação. A navegação é unificada; os bancos e modelos ainda não são um sistema totalmente interoperável.</p></div></section>
 <section class="about-values"><div class="wrap"><div class="section-heading center"><span class="eyebrow-small">Princípios de produto</span><h2>Compromissos que vêm antes da tecnologia</h2></div><div class="value-grid">
 <article><span>{icon('book')}</span><h3>Linguagem simples</h3><p>Explicações diretas para pessoas com diferentes níveis de familiaridade digital.</p></article>
 <article><span>{icon('shield')}</span><h3>Transparência</h3><p>Informamos fontes, limites de dados, cadastros ainda não validados e simulações.</p></article>
 <article><span>{icon('users')}</span><h3>Inclusão</h3><p>Experiência responsiva e atenção à leitura, contraste e navegação por teclado.</p></article>
 </div></div></section>
 <section class="wrap sources"><h2>De onde vêm as informações?</h2><p>Os módulos trabalham com dados e pesquisas de diferentes origens. Nem toda informação é atualizada em tempo real.</p><div class="sources-grid"><div><strong>Saúde e reabilitação</strong><p>CNES e dados geográficos da Secretaria Municipal de Saúde de São Paulo para parte das UBS. Outras categorias exigem validação adicional.</p></div><div><strong>Comunidade e clima</strong><p>Dados históricos INMET, distritos oficiais e referências do OpenStreetMap; algumas análises usam cenários simulados.</p></div></div><p class="source-warning">AVIVA é um protótipo acadêmico. Não substitui atendimento profissional, serviços públicos ou canais de emergência.</p></section>
'''

login=f'''
 <section class="login-layout wrap"><div class="login-intro"><span class="eyebrow"><span class="eyebrow-dot"></span> Seu espaço no AVIVA</span><h1>Bem-vindo <span>de volta.</span></h1><p>Estamos preparando uma experiência pessoal com serviços e informações do seu território. Enquanto isso, você pode explorar o aplicativo sem criar uma conta.</p><div class="login-scene"><img src="/assets/comunidade-aquarela.webp" alt="Pessoas de diferentes gerações em uma convivência coletiva."></div></div><div class="login-card"><div class="card-emblem">{icon('lock')}</div><h2>Entrar no AVIVA</h2><p class="login-card-subtitle">O acesso com senha ainda não está disponível nesta demonstração.</p><div class="demo-notice">{icon('info')}<span>Modo demonstrativo: não informe senhas nem dados pessoais.</span></div><button type="button" class="btn btn-green btn-full" id="visitor-login">Continuar como visitante {icon('arrow')}</button><p class="login-small">Você poderá consultar as áreas abertas do AVIVA sem cadastro.</p><a href="/sobre/" class="subtle-link">Saiba mais sobre o projeto</a></div></section>
'''

pages={
 'index.html':base('Início','Início',home,'Comunidade, saúde e informação mais perto de você. Serviços e orientações em um só lugar.'),
 'auxilios.html':base('Auxílios','Auxílios',auxilios,'Saúde, reabilitação, comunidade e dados do território no AVIVA.'),
 'sobre.html':base('Sobre','Sobre',sobre,'Conheça o AVIVA, suas fontes e os princípios de tecnologia social.'),
 'login.html':base('Login','Login',login,'Área demonstrativa de entrada do AVIVA.')
}
for name,text in pages.items(): (ROOT/name).write_text(text,encoding='utf-8')
print('Written pages:',[(k,len(v)) for k,v in pages.items()])

(()=>{
 'use strict';
 const menuButton=document.querySelector('.menu-toggle');
 const mobileNav=document.getElementById('mobile-nav');
 if(menuButton&&mobileNav){
  const close=()=>{mobileNav.hidden=true;menuButton.setAttribute('aria-expanded','false');menuButton.setAttribute('aria-label','Abrir menu')};
  menuButton.addEventListener('click',()=>{let opening=mobileNav.hidden; mobileNav.hidden=!opening;menuButton.setAttribute('aria-expanded',String(opening));menuButton.setAttribute('aria-label',opening?'Fechar menu':'Abrir menu')});
  document.addEventListener('keydown',e=>{if(e.key==='Escape')close()});
  mobileNav.querySelectorAll('a').forEach(link=>link.addEventListener('click',close));
 }
 const search=document.querySelector('#filter-services');
 if(search){
  const cards=[...document.querySelectorAll('#filtered-services .service-card')];
  const msg=document.querySelector('#no-results');const count=document.querySelector('#service-count');
  const normal=s=>s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
  search.addEventListener('input',()=>{
   const term=normal(search.value.trim());let shown=0;
   for(const card of cards){const visible=normal(card.textContent).includes(term);card.hidden=!visible;if(visible)shown++;}
   msg.hidden=shown!==0;
   count.textContent=shown===1?'1 área encontrada':`${shown} áreas encontradas`;
  });
 }
 const loginButton=document.querySelector('#visitor-login');
 if(loginButton)loginButton.addEventListener('click',()=>{sessionStorage.setItem('aviva_demo_visitante','1');window.location.assign('/auxilios/')});
 if('serviceWorker' in navigator){window.addEventListener('load',()=>navigator.serviceWorker.register('/sw.js').catch(()=>{}))}
})();

"""Ponto de entrada unificado para o portal AVIVA e os módulos internos.

Encaminha o painel Comunidade a um servidor HTTP local e integra as rotas
de reabilitação da aplicação FastAPI em um único endereço de navegação.
Execução local de referência, sem infraestrutura de produção nem dados sensíveis.
"""
from __future__ import annotations
import argparse
import asyncio
from pathlib import Path
import sys
import threading
from urllib.parse import urlencode

import httpx
from starlette.responses import Response, FileResponse
import uvicorn

ROOT = Path(__file__).resolve().parent
SITE = ROOT / 'site'
PAGES = {'/':'index.html','/inicio':'index.html','/inicio/':'index.html','/auxilios':'auxilios.html','/auxilios/':'auxilios.html','/sobre':'sobre.html','/sobre/':'sobre.html','/login':'login.html','/login/':'login.html'}
CONTENT_TYPES = {'.css':'text/css','.js':'application/javascript','.png':'image/png','.webp':'image/webp','.svg':'image/svg+xml','.webmanifest':'application/manifest+json'}
COMUNIDADE = ROOT / 'modulos' / 'comunidade'
REABILITACAO = ROOT / 'modulos' / 'reabilitacao'
sys.path.insert(0, str(COMUNIDADE))
sys.path.insert(0, str(REABILITACAO))
from aviva.web import ServidorAviva  # noqa: E402
from app.main import app as health_app  # noqa: E402


# O aplicativo ASGI distribui requisições entre páginas, arquivos e módulos.
class PortalAVIVA:
    def __init__(self, community_port: int):
        self.community_url = f'http://127.0.0.1:{community_port}'

    async def __call__(self, scope, receive, send):
        if scope['type'] == 'lifespan':
            while True:
                msg = await receive()
                if msg['type'] == 'lifespan.startup':
                    await send({'type': 'lifespan.startup.complete'})
                elif msg['type'] == 'lifespan.shutdown':
                    await send({'type': 'lifespan.shutdown.complete'})
                    return
        elif scope['type'] == 'http':
            path = scope.get('path', '/')
            if path in PAGES or path == '/manifest.webmanifest' or path == '/sw.js' or path.startswith('/assets/'):
                if scope['method'] not in ('GET','HEAD'):
                    return await Response('Método não permitido', status_code=405)(scope,receive,send)
                if path in PAGES:
                    file_path = SITE / PAGES[path]
                elif path == '/manifest.webmanifest':
                    file_path = SITE / 'manifest.webmanifest'
                elif path == '/sw.js':
                    file_path = SITE / 'sw.js'
                else:
                    # Static files are strictly limited to direct names under site/assets.
                    name = path[len('/assets/'):]
                    if not name or '/' in name or '\\' in name or name.startswith('.'):
                        return await Response('Arquivo não encontrado', status_code=404)(scope,receive,send)
                    file_path = SITE / 'assets' / name
                if not file_path.is_file():
                    return await Response('Arquivo não encontrado', status_code=404)(scope,receive,send)
                media = CONTENT_TYPES.get(file_path.suffix)
                return await FileResponse(file_path,media_type=media)(scope,receive,send)
            elif path in ('/comunidade','/comunidade/'):
                inner = dict(scope)
                inner['path'] = '/'
                inner['raw_path'] = b'/'
                await self._forward_community(inner, receive, send)
            elif path == '/reabilitacao' or path.startswith('/reabilitacao/'):
                inner = dict(scope)
                inner['path'] = path[len('/reabilitacao'):] or '/'
                inner['raw_path'] = inner['path'].encode('utf-8')
                await health_app(inner, receive, send)
            elif path.startswith('/api/v1/reabilitacao/') or path.startswith('/static/'):
                await health_app(scope, receive, send)
            else:
                await self._forward_community(scope, receive, send)
        else:
            await Response('Tipo de conexao nao suportado', status_code=400)(scope, receive, send)

    async def _forward_community(self, scope, receive, send):
        parts = []
        while True:
            event = await receive()
            if event['type'] == 'http.disconnect':
                return
            if event['type'] != 'http.request':
                continue
            parts.append(event.get('body', b''))
            if not event.get('more_body', False):
                break
        body = b''.join(parts)
        query = scope.get('query_string', b'').decode('latin-1')
        path = scope.get('path', '/')
        url = self.community_url + path + (('?' + query) if query else '')
        headers = {k.decode('latin-1'): v.decode('latin-1') for k,v in scope.get('headers', [])
                   if k.lower() not in (b'host', b'connection', b'content-length', b'accept-encoding')}
        try:
            async with httpx.AsyncClient(timeout=20.0, trust_env=False) as client:
                upstream = await client.request(scope['method'], url, content=body,
                                               headers={**headers, 'accept-encoding': 'identity'})
        except httpx.HTTPError:
            return await Response('Modulo Comunidade temporariamente indisponivel',status_code=502)(scope,receive,send)
        forwarded = {k:v for k,v in upstream.headers.items()
                     if k.lower() not in ('transfer-encoding','content-length','content-encoding','connection')}
        response = Response(content=upstream.content,status_code=upstream.status_code,headers=forwarded)
        await response(scope,receive,send)


def main():
    parser = argparse.ArgumentParser(description='AVIVA unificado - acesso local em um unico endereco')
    parser.add_argument('--port',type=int,default=8000)
    parser.add_argument('--host',default='127.0.0.1')
    a = parser.parse_args()
    community = ServidorAviva(('127.0.0.1', 0))
    thread = threading.Thread(target=community.serve_forever, daemon=True, name='AVIVA-Comunidade')
    thread.start()
    print('AVIVA: portal visual, Comunidade e Reabilitação no mesmo endereço')
    print(f'Abra no navegador: http://{a.host}:{a.port}/')
    print(f'Páginas: /, /auxilios/, /sobre/, /login/')
    print(f'Modulos: http://{a.host}:{a.port}/comunidade/ e /reabilitacao/')
    print('Atenção: prototipo local - nao tratar dados pessoais ou clinicos reais.')
    try:
        uvicorn.run(PortalAVIVA(community.server_address[1]),host=a.host,port=a.port,log_level='info')
    finally:
        community.shutdown()
        community.server_close()


if __name__ == '__main__':
    main()

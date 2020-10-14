''' SmartLogin Kubernetes PoC  webserver'''
import socket
from aiohttp import web


async def handle_view(request):
    output = socket.getfqdn()
    return web.json_response({"Respuesta de:": output})

app = web.Application()
app.add_routes([web.get('/', handle_view)])

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=8000)

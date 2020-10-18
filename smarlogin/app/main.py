''' SmartLogin Kubernetes PoC  webserver'''
import json
import socket
import time

from aiohttp import web
from prometheus_client import Summary, Counter, Histogram, Gauge
from prometheus_client.core import CollectorRegistry
import prometheus_client


_INF = float("inf")

graphs = {}
graphs['c'] = Counter('slpocapp_request_operations_total',
                      'The total number of processed requests',
                      ['namespace', 'pod'])
graphs['h'] = Histogram('slpocapp_request_duration_seconds',
                        'Histogram for the duration in seconds.', ['namespace', 'pod'], buckets=(1, 2, 5, 6, 10, _INF))


async def handle_view(request):
    start = time.time()
#     graphs['c'].inc()
    output = socket.getfqdn()
#     time.sleep(0.600)
    end = time.time()
    graphs['c'].labels(namespace='default', pod=output).inc()
    graphs['h'].labels(namespace='default', pod=output).observe(end - start)
#     graphs['h'].observe(end - start)
    output = str(output) + ' ' + "processing time: " + str(end)
    return web.json_response({"Respuesta de:": output})


async def handle_view_metrics(request):
    res = []
    for k, v in graphs.items():
        res.append(prometheus_client.generate_latest(v))

    output = ''
    output = output.join(list(map(lambda s: s.decode('UTF-8'), res)))

    return web.Response(body=output)

app = web.Application()
app.add_routes([web.get('/', handle_view)])
app.add_routes([web.get('/metrics', handle_view_metrics)])

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=8000)

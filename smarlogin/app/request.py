import requests

ip = 'http://<IP EXTERNA>/'

while True:
    req = requests.get(ip)
    print(req.text)

import requests

# ip = 'http://<IP EXTERNA>/'
ip = 'http://10.108.52.194/'

while True:
    req = requests.get(ip)
    print(req.text)

import requests

# ip = 'http://<IP EXTERNA>/'
ip = 'http://10.109.102.89/'

while True:
    req = requests.get(ip)
    print(req.text)

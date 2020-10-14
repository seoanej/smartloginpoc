# Introduccion a Docker - Kubernetes

Este es un pequeño PoC para comprobar la potencia y versatilidad de una tecnología estendida dentro del mundo del desarrollo como son los contenedores docker y un orquestador como kubernetes.

## Levantar el proyecto


### Servidor local
1. Instalar un entorno virtual compatible con la versión de python: <br>
- Seguir estas instrucciones para entorno Linux/Mac: <br>
https://github.com/pyenv/pyenv-virtualenv (si ya usas un gestor de entornos virtuales no hagas este paso) <br>
2. Crea un entorno virtual con python 3.8
3. Una vez activado el entorno virtual en un terminal, navega hasta la raíz del proyecto y ejecuta: <br>
~$: ` pip install -r app/requirements.txt` <br>
~$: ` python main.py` <br>
4. Ve a tu navegador habitual y accede a la url propuesta por AioHTTP; si se ha configurado correctamente la respuesta en tu navegador, debe ser tu localhost. 
5. Ejecuta ` Ctrl + c ` en el terminal para finalizar la ejecución. 


### Docker
1. Instalar Docker en tu maquina local: <br>
- Seguir estas instrucciones: <br>
https://docs.docker.com/engine/install/ (si ya tienes Docker instalado no hagas este paso)<br>
2. Abre un terminal en la raíz del proyecto y navega a app/
3. Haz un build de la imagen: <br> ~$: ` docker build -t <image_name> .`
4. Comprueba que tu imagen se ha compilado de forma correcta ejecutando: <br> ~$: ` docker images ` , debería salir ` <image_name> ` en ese listado.
5. Ejecuta la imagen exponiendo un puerto: <br> ~$: `docker run -d -p 8000:8000 --name <container_name> <image_name>:latest`
6. Comprueba que el contenedor esta listo para usarse: <br>~$: `docker ps`, en este listado debe aparecer `<container_name>`
7. Ve a tu navegador habitual y comprueba la url: 0.0.0.0:8000
8. Una vez comprobado que el contenedor docker ofrece una respuesta con el host, para el contenedor con <br> ~$: `docker stop <container_id>` <br> y borralo con: <br> ~$: `docker rm <container_id>` 


### Kubernetes
1. Instalar Kubernetes y aplicaciones asociadas (si ya tienes el stack de kubernetes instalado no hagas este paso):<br>
- Instalar kubectl https://kubernetes.io/es/docs/tasks/tools/install-kubectl/
- Instalar minikube https://kubernetes.io/es/docs/tasks/tools/install-minikube/
2. Abre un terminal en la raíz del proyecto: 
- ~$: `minikube start`
- ~$: `kubectl cluster-info dump` (comprobamos que la instalación es correcta)
3. Ejecutamos en un terminal: <br> ~$: `kubectl apply -f ./k8s/pod.yaml`
4. Ejecutamos en un terminal: <br> ~$: `kubectl apply -f ./k8s/deployment.yaml`
5. Ejecutamos en un terminal: <br> ~$: `kubectl apply -f ./k8s/service.yaml`
6. Comprobamos que todos nuestros objetos están corriendo de forma normal: <br> ~$: `kubectl get all` , el output debe ser un listado de nuestros objetos
7. Para exponer una IP EXTERNA actualmente en pending, ejecutamos: <br> ~$: `minikube tunnel` este cmd dependiendo de nuestra configuración nos pedira confirmación con contraseña.
8. En otro terminal volvemos a listar los objetos de kubernetes `kubectl get all` y copiamos la IP EXTERNA en nuestro navegador habitual.
9. Para comprobar el balanceo de carga entre las 10 réplicas del pod copiamos dentro de app/request.py la IP EXTERNA y ejecutamos en un terminal: <br> ~$: `python3 app/request.py`, comprobando así que cada respuesta es ofrecida por distintos hosts.


Enjoy it.
# Kubernetes HPA, Metricas customizadas, y prometheus

Aqui se cubre cómo almacenar métricas personalizadas con prometheus y cómo usarlo para escalar con el escalador automático de pod horizontal en Kubernetes

Descripción general de la arquitectura
--------------------------------------

Usamos el adaptador de Prometheus para extraer métricas personalizadas de nuestra instalación de Prometheus y luego dejamos que el escalador automático de pods horizontal (HPA) lo use para escalar los pods hacia arriba o hacia abajo.

![Escalación automática arquitectura](images/auto-scaling-architecture.png)

Adjustar  el servidor de muestra
--------------------------------

Primero, cambiamos el servidor 'main.py' (Prometheus cliente) de tal manera que se pueda instrumentar las metricas que prometheus tiene que recolectar incluyendo datos a que namespace y pods de Kubernetes estamos instrumentando.

- Probamos los cambios activando el entorno virtual de python en la terminal, navegando hasta la raíz del proyecto y luego en el archivo "app" y ejecutando:

```console
> pip install -r requirements.txt  <-- prometheus-client has been added
> python main.py
```

- Prueba que el servidor esta funcianando correctamente en tu navegador:
`[http://localhost:8000](http://localhost:8000)`
Si funciona tendras un mensaje como:
`Respuesta de:   "laptop-jaime processing time: 1603020844.3325272"`

- Prueba que el servidor esta produción metricas para colectar en prometheus:
`[http://localhost:8000/metrics](http://localhost:8000/metrics)`
Si funciona tendras un mensaje como:

```console
# HELP slpocapp_request_operations_total The total number of processed requests
# TYPE slpocapp_request_operations_total counter
slpocapp_request_operations_total{namespace="default",pod="laptop-jaime"} 1.0
# HELP slpocapp_request_operations_created The total number of processed requests
# TYPE slpocapp_request_operations_created gauge
slpocapp_request_operations_created{namespace="default",pod="laptop-jaime"} 1.6030208443325655e+09
# HELP slpocapp_request_duration_seconds Histogram for the duration in seconds.
# TYPE slpocapp_request_duration_seconds histogram
slpocapp_request_duration_seconds_bucket{le="1.0",namespace="default",pod="laptop-jaime"} 1.0
slpocapp_request_duration_seconds_bucket{le="2.0",namespace="default",pod="laptop-jaime"} 1.0
slpocapp_request_duration_seconds_bucket{le="5.0",namespace="default",pod="laptop-jaime"} 1.0
slpocapp_request_duration_seconds_bucket{le="6.0",namespace="default",pod="laptop-jaime"} 1.0
slpocapp_request_duration_seconds_bucket{le="10.0",namespace="default",pod="laptop-jaime"} 1.0
slpocapp_request_duration_seconds_bucket{le="+Inf",namespace="default",pod="laptop-jaime"} 1.0
slpocapp_request_duration_seconds_count{namespace="default",pod="laptop-jaime"} 1.0
slpocapp_request_duration_seconds_sum{namespace="default",pod="laptop-jaime"} 0.0011820793151855469
# HELP slpocapp_request_duration_seconds_created Histogram for the duration in seconds.
# TYPE slpocapp_request_duration_seconds_created gauge
slpocapp_request_duration_seconds_created{namespace="default",pod="laptop-jaime"} 1.6030208443325946e+09
```
Desplegar el servidor como un contenedor en Kubernetes
------------------------------------------------------

- Primero construimos la imagen del contenedor y empujamos al repository de docker hub:

```console
> docker build -t jseoane/slpocapp:latest .
> docker push jseoane/slpocapp
```
La imagen empujada a docker hub is la que Kubernetes necesita bajar cuando se este creando un despliego en el cluster con un "Deployment

- Comenzamos Kubernetes minikube y su correspondiente dashboard:

```console
> minikube start
> minikube dashboard &> dashboard.out &
> cd ../k8s
> kubectl apply -f deployment.yaml
> kubectl apply -f service.yaml
> minikube tunnel &> tunnel.out &
> kubectl get deploy app
> kubectl get pods
> kubectl get svc app-service
> minikube service app-service
```
Si todo fue bien, se despliega la application en dos pods en un contenedor en cada uno. Tambien se habilita un distribuidor de cardo (loadbalancer) y se able la applicación en el navegador.

- verificamos que la application funciona y que metricas se estan exponiendo:

```console
http://<app-service external IP>/
http://<app-service external IP>/metrics
```

Instalar Helm gestionador de Kubernetes apps
--------------------------------------------

Instalamos Helm para gestionar las aplicaciones a instalar en Kubernetes como: prometheus, prometheus adapter y grafana.

```console
> curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3
> chmod 700 get_helm.sh
> ./get_helm.sh
```

Activar el servidor de metricas de Kubernetes
---------------------------------------------
Activamos el servidor de metricas de Kubernetes para que colecte metrics de los recursos en Kubernetes y para intercambiar metricas con prometheus

```console
> minikube addons enable metrics-server
> minikube addons list
```

Preparar la configuracion adicional para raspado de Prometheus
--------------------------------------------------------------
- Cambiamo de directorio a "prometheus". Aqui creamos el archivo "prometheus-additional.yaml" con la configuracion adicional para raspar las metricas de nuestro servidor. Por ejemplo:

```console
- job_name: "servidor-custom-metrics"
  static_configs:
  - targets: ["10.109.102.89:80"]
```
- Generar un secreto de esta configuración:

```console
> kubectl create secret generic additional-scrape-configs --from-file=prometheus-additional.yaml --dry-run=client -o yaml > additional-scrape-configs.yaml
```
- Añadir el secreto a Kubernetes:

```console
> kubectl apply -f additional-scrape-configs.yaml
```

Instalar y configurar Prometheus Operator en Kubernetes
------------------------------------------
Installamos Prometheus Operator para colectar metricas de la aplicación de prueba que hemos instalado a travez de la ruta '/metrics' del servidor 

- Añadimos el repositorio "bitnami" siendo disponible a Helm

```console
> helm repo add bitnami https://charts.bitnami.com/bitnami

```

- Cambiamos de directorio a "prometheus" donde se encuentra el archivo "custom-metrics.yaml" que especifica el URL donde prometheus puede acceder a las metricas de nuestro servidor.

```console
> cd ../prometheus
> helm install prometheus --set prometheus.scrapeInterval=15s --set prometheus.evaluationInterval=15s --set prometheus.additionalScrapeConfigsExternal.enabled=true --set prometheus.additionalScrapeConfigsExternal.name=additional-scrape-configs --set prometheus.additionalScrapeConfigsExternal.key=prometheus-additional.yaml bitnami/kube-prometheus
```

- Habilitar port forwarding para poder acceder el Dashboard de prometheus y del gestionador de alertas

```console
> kubectl port-forward svc/prometheus-kube-prometheus-prometheus 9090 &> prometheous-dashboard.out &
> kubectl port-forward svc/prometheus-kube-prometheus-alertmanager 9093:9093 &> alert-manager-dashboard.out &
```

- Comprobar si prometheus esta rastreando las metricas del servidor en el Dashboard:

```console
http://localhost:9090/targets
```
Tambien se puede comprobar que las metricas son registradas en prometheus en el Dashboard escribiendo el nomber de la merica especificas en el campo "Expression (e.g. "slpocapp_"):

```console
http://localhost:9090/graphs
```

Instalar y configurar Grafana en Kubernetes
-------------------------------------------
Instalamos Grafana que es una interfaz grafica avanzada para visualizar los datos recolectados por prometheus.

- Instalamos grafana con Helm:

```console
> helm install grafana bitnami/grafana
```

- Accedemos a grafana
```console
> kubectl port-forward svc/grafana 8080:3000 &> grafana-dashboard.out &
> echo "Password: $(kubectl get secret grafana-admin --namespace default -o jsonpath="{.data.GF_SECURITY_ADMIN_PASSWORD}" | base64 --decode)"
> firefox http://localhost:8080/login
```

- Configuramos Grafana para extraer datos de prometheous y ilustrarlos en un Dashboard para nuestro servidor:

* En el panel izquierdo abrimos "Configuration->Data Sources", le damos a "Add data source", elegimos "Prometheus" y ponemos el IP (kubectl get svc/prometheus-kube-prometheus-prometheus -o jsonpath='{.spec.clusterIP}) of the prometheous service el campo "URL" ex: http://10.99.145.65:9090 y le damos al boton "Save & Test"

* En el panel izquierdo abrimos "Dashboard->Manage", damos al boton "Import", damos al boton "Upload JSON file", abrimoso el archivo "grafana/slpocapp-custom-metrics-dashboard.md" y le damos a "Import". Ahora podemos ver el Dashboard con dos paneles visualizando las cargas en los pos.

* Si Comenzamos el cliente "python apps/requests.py", tendriamos que ver los lecturas de los datos cambiando en los paneles.


Para que kubernetes pueda proveer las metricas de prometheus al auto escalador horizontal, se necesita instalar el adaptador de prometheus:

- Cambiamos al archivo "adapter" donde se encuntra la configuracion del adaptador en el archivo "values.xml" de tal manera que solicite las metricas del servicio prometheus y que se expongan a travez del custom.metrics.api en kubernetes para darle asi acceso al auto escalador. E instalamos el adaptador con Helm con esta configuracion:
Instalar y configurar prometheus adapter en Kubernetes
------------------------------------------------------

```console
> cd adapter
> helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
>  helm install prometheus-adapter -f values.yaml prometheus-community/prometheus-adapter

```

- Verficamos que recibimos metricas a travez del adaptador:

```console
kubectl get --raw /apis/custom.metrics.k8s.io/v1beta1 | jq
```

- ejemplo de emission:

```console
{
  "kind": "APIResourceList",
  "apiVersion": "v1",
  "groupVersion": "custom.metrics.k8s.io/v1beta1",
  "resources": [
    {
      "name": "pods/slpocapp_request_operations_per_second",
      "singularName": "",
      "namespaced": true,
      "kind": "MetricValueList",
      "verbs": [
        "get"
      ]
    },
    {
      "name": "namespaces/slpocapp_request_operations_per_second",
      "singularName": "",
      "namespaced": false,
      "kind": "MetricValueList",
      "verbs": [
        "get"
      ]
    }
  ]
}
```

- Comprobamos que kubernetes esta recibiendo metricas de nuestro servidor:

```console
> kubectl get --raw "/apis/custom.metrics.k8s.io/v1beta1/namespaces/default/pods/*/slpocapp_request_operations_per_second" | jq 
```
- Ejemplo de emission

```console
{
  "kind": "MetricValueList",
  "apiVersion": "custom.metrics.k8s.io/v1beta1",
  "metadata": {
    "selfLink": "/apis/custom.metrics.k8s.io/v1beta1/namespaces/default/pods/%2A/slpocapp_request_operations_per_second"
  },
  "items": [
    {
      "describedObject": {
        "kind": "Pod",
        "namespace": "default",
        "name": "app-688f6c5b76-h5gp7",
        "apiVersion": "/v1"
      },
      "metricName": "slpocapp_request_operations_per_second",
      "timestamp": "2020-10-18T16:24:01Z",
      "value": "0",
      "selector": nullkubectl describe hpa app
    }
  ]
}
```

Desplegar la configuracion de HPA auto escalador
------------------------------------------------
Desplegamos una configuracion de HPA auto escalador para nuestro servidor usando las metricas personalizadas:

```console
> cd ../../k8s
> kubectl apply -f deployment-hpa.yaml
> kubectl describe hpa app
```

Si fue configurado propiamente la emission sTeria: 

```console
AbleToScale     True    ScaleDownStabilized  recent recommendations were higher than current one, applying the highest recent recommendation
ScalingActive   True    ValidMetricFound     the HPA was able to successfully calculate a replica count from pods metric slpocapp_request_operations_per_second
```

Probar el auto escalador
-------------------------
Para probar el escalador monitoreamos el servicio hpa y los pods al mismo tiempo de que empezamos a mandar cargas con el cliente requests.py de tal manera que el numero de pods aumentan de 2 a 6 cuando se aumenta la carga y se rebaja a dos pods cuando paramosparamos e el cliente

- Emission antes de comenzar el cliente

```console
> kubectl get -w pods
NAME                                                     READY   STATUS    RESTARTS   AGE
alertmanager-prometheus-kube-prometheus-alertmanager-0   2/2     Running   0          126m
app-688f6c5b76-b5fs5                                     1/1     Running   0          20s
app-688f6c5b76-nqscl                                     1/1     Running   0          20s
prometheus-adapter-76fb8b6f77-qndx2                      1/1     Running   0          48m
prometheus-kube-prometheus-operator-7f8896bb67-z85zg     1/1     Running   0          126m
prometheus-kube-state-metrics-6ccc976f4-sbr85            1/1     Running   0          126m
prometheus-node-exporter-vw9cz                           1/1     Running   0          126m
prometheus-prometheus-kube-prometheus-prometheus-0       3/3     Running   1          125m
```

```console
> kubectl get -w hpa
NAME   REFERENCE        TARGETS       MINPODS   MAXPODS   REPLICAS   AGE
app    Deployment/app   <unknown>/2   2         6         0          6s
app    Deployment/app   <unknown>/2   2         6         2          16s
```

- Emission despues de comenzar el cliente depues de 1 minuto de carga
```console
NAME                                                     READY   STATUS    RESTARTS   AGE
alertmanager-prometheus-kube-prometheus-alertmanager-0   2/2     Running   0          132m
app-688f6c5b76-4ljrb                                     1/1     Running   0          45s
app-688f6c5b76-b5fs5                                     1/1     Running   0          6m21s
app-688f6c5b76-n2qhw                                     1/1     Running   0          45s
app-688f6c5b76-nqscl                                     1/1     Running   0          6m21s
app-688f6c5b76-t7qsw                                     1/1     Running   0          59s
app-688f6c5b76-xzcwr                                     1/1     Running   0          59s
prometheus-adapter-76fb8b6f77-qndx2                      1/1     Running   0          54m
prometheus-kube-prometheus-operator-7f8896bb67-z85zg     1/1     Running   0          132m
prometheus-kube-state-metrics-6ccc976f4-sbr85            1/1     Running   0          132m
prometheus-node-exporter-vw9cz                           1/1     Running   0          132m
prometheus-prometheus-kube-prometheus-prometheus-0       3/3     Running   1          131m


NAME   REFERENCE        TARGETS       MINPODS   MAXPODS   REPLICAS   AGE
app    Deployment/app   <unknown>/2   2         6         0          6s
app    Deployment/app   <unknown>/2   2         6         2          16s
app    Deployment/app   32775m/2      2         6         2          2m46s
app    Deployment/app   46481m/2      2         6         4          3m1s
app    Deployment/app   53862m/2      2         6         6          3m16s


```

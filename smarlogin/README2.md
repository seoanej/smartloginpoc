# Configuracion - Kubernetes Auto escalacion horizontal


    Add aliases to /ect/hosts for simple access:

    Determine actual ip with minikube ip

192.168.99.100  minikube.local prometheus.local alertmanager.local grafana.local

* Install Helm

curl https://raw.githubusercontent.com/kubernetes/helm/master/scripts/get-helm-3 > get_helm.sh
chmod 700 get_helm.sh
./get_helm.sh

>> minikube addons enable metrics-server

Installed Prometheus Operator from [Bitnami repos](https://bitnami.com/stack/prometheus-operator/helm) and the charts details including kubernetse manifests can be found in GitHub [here](https://github.com/bitnami/charts/tree/master/bitnami/kube-prometheus) and in the local repo in thel helm folder.

Add bitname repo to helm
>> helm repo add bitnami https://charts.bitnami.com/bitnami

Install Prometheous Operator in Minikube:
>> helm install my-release bitnami/kube-prometheus

Run to enable access to Prometheus Dashboard from outside cluster:
>> echo "Prometheus URL: http://127.0.0.1:9090/"
>> kubectl port-forward --namespace monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090

Run to enable access to Prometheus Alert Manager Dashboard from outside cluster:
>> echo "Alertmanager URL: http://127.0.0.1:9093/"
>> kubectl port-forward --namespace monitoring svc/prometheus-kube-prometheus-alertmanager 9093:9093

Added prometheus-client to python requirements dependencies


RESOURCES:
[Digital Ocean - How To Set Up a Kubernetes Monitoring Stack with Prometheus, Grafana and Alertmanager on DigitalOcean](https://www.digitalocean.com/community/tutorials/how-to-set-up-a-kubernetes-monitoring-stack-with-prometheus-grafana-and-alertmanager-on-digitalocean#step-6-%E2%80%94-configuring-the-monitoring-stack-optional)
[RedHat - An introduction to installing Prometheus with Minikube](https://www.redhat.com/sysadmin/installing-prometheus)
[github - prometheus-grafana-on-minikube](https://github.com/baralc/prometheus-grafana-on-minikube)
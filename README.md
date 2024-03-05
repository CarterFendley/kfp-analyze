# kfp-analyze

> NOTES:
> - This is an experimental library, do not place a hard dependency on this unless you may be willing to fork it in the future.
> - This library is currently only tested with KFP `1.8.18`

## Installation

If you want Graphviz functionality you must install the binaries via instructions [here](https://www.graphviz.org/download/)

## Development setup

```
pip install -e .
```

### Kubeflow Setup

> These instructions are vaguely based on the ones provided: [one](https://www.kubeflow.org/docs/components/pipelines/v1/installation/localcluster-deployment/), [two](https://www.kubeflow.org/docs/components/pipelines/v1/installation/standalone-deployment/), [three](https://v0-7.kubeflow.org/docs/other-guides/virtual-dev/getting-started-minikube/), by Kubeflow

First, perquisites

1. Install kubectl: [instructions](https://kubernetes.io/docs/tasks/tools/#kubectl)
2. Install minikube: [instructions](https://minikube.sigs.k8s.io/docs/start/)

Then make sure you do not have a previous minikube session running, and start a fresh session with
> Note: The `--kubernetes-version=v1.20.15` due to the issues with subsequent `kubetctl apply` commands related to KFP `v1.8.18` see [here](https://github.com/kubeflow/manifests/issues/2028)

```bash
minikube stop
minikube delete
minikube start --cpus 4 --memory 8096 --disk-size=40g --kubernetes-version=v1.20.15
```

Install KFP standalone, here I install `1.8.18`

```
export PIPELINE_VERSION=1.8.18
kubectl apply -k "github.com/kubeflow/pipelines/manifests/kustomize/cluster-scoped-resources?ref=$PIPELINE_VERSION"
kubectl wait --for condition=established --timeout=60s crd/applications.app.k8s.io
kubectl apply -k "github.com/kubeflow/pipelines/manifests/kustomize/env/platform-agnostic-pns?ref=$PIPELINE_VERSION"
```

View the Kubeflow UI by port forwarding and visiting [http://localhost:8080/](http://localhost:8080/)
```
kubectl port-forward -n kubeflow svc/ml-pipeline-ui 8080:80
```

And connect with an sdk client via the follow

**NOTE:** There may be sometime after startup for which this will `504`

```python
from kfp import Client

client = Client(host='http://localhost:8080')
```
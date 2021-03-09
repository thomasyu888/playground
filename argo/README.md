# Argo Exploration

Make sure you kubernetes is set up first.  Follow instructions [here](https://thomasyu888.github.io/playground/kubernetes/) on how to set up a kubernetes cluster.

1. Follow instructions [here](https://argoproj.github.io/argo-workflows/quick-start/) to create the argo namespace on kubernetes. This was the clusterrolebinding command I ran.
    ```
    kubectl create clusterrolebinding tyu-cluster-admin-binding --clusterrole=cluster-admin --user=thomas.yu@sagebase.com
    ```
    If the argo namespace already exists (check if it exists by running `kubectl get namespace`, more on [namespaces](https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/)
1. View the Argo dashboard
    ```
    kubectl -n argo port-forward deployment/argo-server 2746:2746
    localhost:2746
    ```
1. Submit test Argo job
    ```
    argo submit -n argo --watch https://raw.githubusercontent.com/argoproj/argo/master/examples/hello-world.yaml
    argo list -n argo
    argo get -n argo @latest
    argo logs -n argo @latest
    ```



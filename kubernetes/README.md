# Kubernetes Exploration

## Accessing Kubernetes

After setting up the kubernetes cluster on AWS EKS, follow these instructions to access the kubernetes cluster.  I created a kubernetes cluster called `tom-test`, which you should be able to see after logging into AWS via jumpcloud.

1.  To access the kubernetes cluster on AWS EKS, one must have access to the aws account. Follow these [instructions](https://sagebionetworks.jira.com/wiki/spaces/IT/pages/405864455/Jumpcloud) under section, 'AWS CLI with Jumpcloud credentials
'.
1.  Start conda environment that has `aws-cli` and `kubectl`
    ```
    conda activate aws
    ```
1.  After you confirm access aws by running:
    ```
    aws --profile sandbox-developer s3api list-buckets
    ```
    You now have to create a [kubernetes configuration](https://docs.aws.amazon.com/eks/latest/userguide/create-kubeconfig.html).  Running this command will create a kubernetes config file at `~/.kube/config`
    ```
    aws eks --region us-east-1 update-kubeconfig --name tom-test --profile sandbox-admin
    ```
1. Check if you have access to kubernetes.
    ```
    kubectl get svc
    ```

## Using Kubernetes

### Deploying a Kubernetes dashboard
* Deploy dashboard - https://kubernetes.io/docs/tasks/access-application-cluster/web-ui-dashboard/
* Create service account - https://github.com/kubernetes/dashboard/blob/master/docs/user/access-control/creating-sample-user.md

### Deploying spark with Helm
https://medium.com/@tomlous/deploying-apache-spark-jobs-on-kubernetes-with-helm-and-spark-operator-eb1455930435

### Deploying your own application
...



### Common Kubernetes functions

```
# Get namespaces
kubectl get namespaces
# Get pods of a namespace
kubectl get pods -n default
# Figure out what is wrong with pods
kubectl describe pods podnamehere
# Get pods associated with a app
kubectl get pods -l app=servicename
# remove config map
kubectl delete configmap funnel-config
# Restarting a service
kubectl rollout restart deployment yourservice
```

# Kubernetes Exploration

## Accessing Kubernetes

After setting up the kubernetes cluster on AWS EKS, follow these instructions to access the kubernetes cluster.  I created a kubernetes cluster called `tom-test`, which you should be able to see after logging into AWS via jumpcloud.

1.  Follow instructions on [aws](https://docs.aws.amazon.com/eks/latest/userguide/create-kubeconfig.html) to set up your `~/.kube/config`.

    ```
    apiVersion: v1
    clusters:
    - cluster:
        certificate-authority-data: # Fill in value here
        server:  # Fill in value here
    name: arn:aws:eks:us-east-1:563295687221:cluster/tom-test
    contexts:
    - context:
        cluster: arn:aws:eks:us-east-1:563295687221:cluster/tom-test
        user: arn:aws:eks:us-east-1:563295687221:cluster/tom-test
    name: arn:aws:eks:us-east-1:563295687221:cluster/tom-test
    current-context: arn:aws:eks:us-east-1:563295687221:cluster/tom-test
    kind: Config
    preferences: {}
    users:
    - name: arn:aws:eks:us-east-1:563295687221:cluster/tom-test
    user:
        exec:
        apiVersion: client.authentication.k8s.io/v1alpha1
        args:
        - --region
        - us-east-1
        - eks
        - get-token
        - --cluster-name
        - tom-test
        command: aws
        env:
        - name: AWS_PROFILE
            value: sandbox-admin
    ```

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

1. Create [docker registry pull secrets](https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account/#add-imagepullsecrets-to-a-service-account)

    ```
    kubectl create secret docker-registry myregistrykey --docker-server=DUMMY_SERVER \
        --docker-username=DUMMY_USERNAME --docker-password=DUMMY_DOCKER_PASSWORD \
        --docker-email=DUMMY_DOCKER_EMAIL
    ```

### Deploying a Kubernetes dashboard

- Deploy dashboard - https://kubernetes.io/docs/tasks/access-application-cluster/web-ui-dashboard/
- Create service account - https://github.com/kubernetes/dashboard/blob/master/docs/user/access-control/creating-sample-user.md

### Deploying spark with Helm

https://medium.com/@tomlous/deploying-apache-spark-jobs-on-kubernetes-with-helm-and-spark-operator-eb1455930435


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

### Deploy cronjobs

https://v1-19.docs.kubernetes.io/docs/tasks/job/automated-tasks-with-cron-jobs/

```
kubectl apply -f cronjob.yaml
kubectl get cronjob
kubectl get jobs --watch
# Replace "hello-4111706356" with the job name in your system
kubectl get pods --selector=job-name=hello-1628671800

```
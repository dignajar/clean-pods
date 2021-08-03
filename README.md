# Kubernetes: Clean pods older than X days
Delete pods older than X days. The python script uses the `Kubernetes API` and the `TOKEN` from a service account to calculate and delete pods older than X days.

I use this Docker for clean up the pods created by Airflow (Kubernetes Operator), when Airflow deploys a pod the pod get the status `Completed` or `Error` and is not delete after complete the task, also I don't want to delete them at the end of the execution because we lost the logs, so execute this Docker as a cronjob every day (at 2am) and delete the pods older than 5 days after the creation time.

## Pod status
The pods can get the following status:
- Pending
- Running
- Succeeded (Completed)
- Failed (Error)
- Unknown

## Cronjob for Kubernetes
- Replace the namespace `demo` for yours.
- Replace the service account `demo-user` for yours.
- The service account need to have permissions for list and delete pods for the namespace defined.
- The environment variable `POD_STATUS` supports a list separated by commas.

Manifest `clean-pods.yaml`
```
apiVersion: batch/v1beta1
kind: CronJob
metadata:
  name: clean-pods
  namespace: demo
  labels:
    app: clean-pods
spec:
  schedule: "00 02 * * *"
  failedJobsHistoryLimit: 1
  successfulJobsHistoryLimit: 1
  jobTemplate:
    spec:
      template:
        spec:
          serviceAccountName: demo-user
          restartPolicy: OnFailure
          containers:
          - name: clean-pods
            imagePullPolicy: Always
            image: dignajar/clean-pods:latest
            env:
              - name: API_URL
                value: "https://kubernetes.default.svc/api/"
              - name: NAMESPACE
                value: "demo"
              - name: MAX_DAYS
                value: "5"
              - name: POD_STATUS
                value: "Succeeded, Failed"
```

## Service account for Kubernetes
Service account for the namespace `demo` with enoght permissions to list and delete pods.

Manifest `service-account.yaml`
```
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: demo-user
  namespace: demo

---
kind: Role
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: demo-user-role
  namespace: demo
rules:
- apiGroups: [""]
  resources: ["pods","pods/exec","pods/log"]
  verbs: ["*"]

---
kind: RoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: demo-user
  namespace: demo
subjects:
- kind: ServiceAccount
  name: demo-user
  namespace: demo
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: demo-user-role
```

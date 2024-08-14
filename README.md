# This is a temporary branch for testing a Buerokratt helm deployment
NOTE:   
`modules.yaml`, `components.yaml` and `post-deploy.yaml` have currently paths set up for testing purposes and do not reflect actual structure until deployment pipeline moves to No-Ops

#### How to run as a test 

Requirements:  

#### Minikube
To run it on your local K8s cluster, a simple `minikube` is sufficent, you can find how to run it here:  
https://minikube.sigs.k8s.io/docs/start/?arch=%2Flinux%2Fx86-64%2Fstable%2Fbinary+download

To install ` kubectl`

```
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
```
```
chmod +x kubectl
```
```
sudo mv kubectl /usr/local/bin/
```

To install `helm`

```
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

To install `longhorn`  
```
helm repo add longhorn https://charts.longhorn.io
```
```
helm repo update
```
```
kubectl create namespace longhorn-system
```
```
helm install longhorn longhorn/longhorn --namespace longhorn-system
```

#### Cloning the repo
To run Buerokratt deployment in a local test environment, first clone the repo:

```
python3 git_clone.py git.yaml
```
You have now cloned Buerokratt helm charts, continue with testing the deployment pipeline(s)
## Helm installation using python 


### Requirements  

#### Cluster requirements
For successful installation, cluster must have  
 - CertManager (not needed for local testing)
 - Istio 
 - Longhorn

#### Python requirements  

`Python3, pip`  

Needed libraries:  

`pyyaml`  

To install use `libraries/install_libraries.py`   

This script can be used in general also to install libraries quickly and keep eye on, what has been installed.  

Use `requirements.json` for adding the libraries you need to install.

#### Preparations 

#### Changing `secrets`

Modify the secrets.yaml to give values to your secrets in values.yaml files.  
Run the script  

```
python3 secrets.py secrets.yaml
```


##### Password (sensitive info) changes

Edit the `passwords.yaml` to give correct info  
Run the script

```
python3 password_change.py passwords.yaml
```


##### Deployment
To deploy all, run 

```
python3 deploy.py components.yaml
```

This will deploy all components in a namespace described in `components.yaml`. Same logic goes also with `modules.yaml` and `post-deploy.yaml`


To deploy only certain components or modules add the release name

```
python3 deploy.py components.yaml component-test
```
or
```
python3 deploy.py modules.yaml module-test
```


##### Post deployment

```
python3 deploy.py post-deploy.yaml
```

##### Deleting deployments

To delete, run a script `uninstall.py`
Depending on directions, you can uninstall all or certain deployments
for example


```
python3 uninstall.py components.yaml
```
This will delete all components in a namespace described in `components.yaml`. Same logic goes also with `modules.yaml` and `post-deploy.yaml`

```
python3 uninstall.py components.yaml component-test
```

This will delete one component in a namespace described in `components.yaml`. Same logic goes also with `modules.yaml` and `post-deploy.yaml`

Note: You can add as many components/modules etc as you need to uninstall.

```
python3 uninstall.py components.yaml component-test component-test2 component-testX
```


#### Things to look out for
While inside the components.yaml, modules.yaml and post-deploy.yaml deployments are in order, be noted, that `component that controls Postgres databases` should always be a first one to be deployed.

When updating the info inside components.yaml, modules.yaml, post-deploy.yaml follow the yaml structure very strictly.  
for example:

```
deployments:
  - name: test
    chart_path: ./
    namespace: test3
  - name: test2
    chart_path: ./
    namespace: test3
```

## Current issues
Deployment script does not have yet a check, that would give `databases` and `opensearch` ample time to start up. Working on it.

### How to use

 Requirements  

`Python3, pip`  

Needed libraries:  

`pyyaml`  

To install use `libraries/install_libraries.py`   

This script can be used in general also to install libraries quickly and keep eye on, what has been installed.  

Use `requirements.json` for adding the libraries you need to install.

##### Preparations  
To change paramaters (domains, passwords etc.) in values.yaml 's  

Apply changes inside `changes.yaml`  

Run `update_values.py`   


##### Deployment
To deploy all, run 

```
python3 deploy.py components.yaml
```

This will deploy all components in a namespace described in `components.yaml`. Same logic goes also with `modules.yaml` and `post-deploy.yaml


To deploy only certain components or modules add the release name

```
python3 deploy.py components.yaml component-byk-ruuter
```
or
```
python3 deploy.py modules.yaml module-byk-backofice-gui
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
python3 uninstall.py components.yaml component-byk-ruuter
```

This will delete one component in a namespace described in `components.yaml`. Same logic goes also with `modules.yaml` and `post-deploy.yaml`

Note: You can add as many components/modules etc as you need to uninstall.

```
python3 uninstall.py components.yaml component-byk-ruuter component-byk-resql component-byk-tim
```


#### Things to look out for
While inside the components.yaml, modules.yaml and post-deploy.yaml deployments are in order, be noted, that `component-databases` should always be a first one to be deployed.

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
Deployment script does not have yet a check, that would give `component-databases` and `component-opensearch-node` ample time to start up. Working on it.
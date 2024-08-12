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
python3 deploy.py components.yaml modules.yaml
```


To deploy only components or modules, use according yaml during installation.
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

NOTES: Deploy Database first. 
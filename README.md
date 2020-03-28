# jib

## Prerequisites

Kubernetes >=1.16.x

Will install Tiller in the cluster if it is not present.

## Installation

```
 ./jib up
```

NOTES:
Thank you for installing JupyterHub!

Your release is named jib and installed into the namespace jib.

You can find if the hub and proxy is ready by doing:

 kubectl --namespace=jib get pod

and watching for both those pods to be in status 'Ready'.

You can find the public IP of the JupyterHub by doing:

 kubectl --namespace=jib get svc proxy-public

It might take a few minutes for it to appear!

Note that this is still an alpha release! If you have questions, feel free to
  1. Read the guide at https://z2jh.jupyter.org
  2. Chat with us at https://gitter.im/jupyterhub/jupyterhub
  3. File issues at https://github.com/jupyterhub/zero-to-jupyterhub-k8s/issues
  

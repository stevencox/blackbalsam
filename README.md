# Blackbalsam

![image](https://user-images.githubusercontent.com/306971/80292483-05426b00-8725-11ea-9ab3-0686c8a6c76a.png)

Blackbalsam is an open source visualization and scalable computing environment providing computation infrastructure with  access to COVID-19 data sets and an emphasis on analytics relating to North Carolina.

## Overview

Blackbalsam provides flexible notebook computing through a JupyterHub interface featuring the ability to dynamically create personal Spark clusters using the underlying Kubernetes infrastructure. The prototype system runs at the [Renaissance Computing Institute](https://renci.org/) on premise and it is cloud ready. 

![image](https://user-images.githubusercontent.com/306971/80296143-80684900-8746-11ea-9ad7-e2dc69d6d71f.png)

### Authentication
Access is provided via GitHub and OpenID Connect (OIDC). Whitelisted users can use their GitHub identity to login and start working immediately.

### Notebook Computing
JupyterHub provides the interface to the environment presenting a notebook providing Python and R kernels.

### Visualization
The Jupyter notebook provides basic visualization via matplotlib, ploty, and seaborn. It also inludes bokeh, [yellowbrick](https://www.scikit-yb.org/en/latest/), and ipyleaflet to handle more specialized needs including machine learning and geographic visualization.
![image](https://user-images.githubusercontent.com/306971/80293212-91579100-872b-11ea-9fe3-d8bd00414794.png)

### Compute
The Jupyter notebook is also instrumented to allow dynamically launching a customized, personal Apache Spark cluster of a user specified size through the Kubernetes API. In this figure, we see the notebook for loading the Python interface to Blackbalsam and creating a four worker Spark cluster. After creating the cluster, it uses Spark's resilient distributed dataset (RDD) interface and its functional programming paradigm to map an operator to each loaded article.
![image](https://user-images.githubusercontent.com/306971/80293315-60c42700-872c-11ea-8b29-6a954bc54e80.png)

The mechanics of configuring and launching the cluster are handled transparently to the user. Exiting the notebook kernel deallocates the cluster. This figure shows the four 1GB Spark workers created by the previous steps.
![image](https://user-images.githubusercontent.com/306971/80293355-ae409400-872c-11ea-94d7-73b50e67bf7a.png)

Creating the Word2Vec model is straightforward:
![image](https://user-images.githubusercontent.com/306971/80293487-c664e300-872d-11ea-809f-454cdb1c395e.png)

### Storage
#### NFS
The network filesystem (NFS) is used to mount shared storage to each user notebook at /home/shared.

#### Object Store
The Minio object store provides an S3 compatible interface .
![image](https://user-images.githubusercontent.com/306971/80293124-8e0fd580-872a-11ea-8643-1bfbd0978368.png)

Minio supports distributed deployment scenarios which make it horizontally scalable. Minio also facilitates loading large objects into Apache Spark
![image](https://user-images.githubusercontent.com/306971/80295919-0a171700-8745-11ea-8060-d32d2fe71468.png)

#### Alluxio Memory Cache
Machine learning and big data workflows, like most, benefit from fast data access. Alluxio is a distributed memory cache interposed between multiple "under-filesystems" like NFS and analytic tools like Spark and its machine learning toolkit. It stores data in node memory, not only accelerating access but allowing failed workflows to restart and other interesting scenarios. It also supports using the Minio S3 object store as an under filesystem. Since Alluxio also supports an ACL based access control model, this creates some interesting possibilities for us to explore with regard to data sharing.

## Prerequisites

* Kubernetes v1.17.4
* kubectl >=v1.17.4
* Python 3.7.x
* A Python virtual environment including yamlpath==2.3.4

## Installation

### Authentication

Create a [GitHub OAuth app](https://developer.github.com/apps/building-oauth-apps/)

### Environment Configuration

Create a file in your home directory called `.blackbalsam` with contents like these:
```
jupyterhub_secret_token=<jupyter-hub-secret-token> 
jupyterhub_baseUrl=/blackbalsam/                  
public_ip=<public-ip-address>                    
github_client_id=<github-client-id>               
github_client_secret=<client-server-id>
github_oauth_callback=http://<your-domain-name>/blackbalsam/oauth_callback 
minio_access_key=<minio-access-key>
minio_secret_key=<minio-secret-key>   
```
### Executing the Install
```
git clone git@github.com:stevencox/blackbalsam.git
cd blackbalsam
bin/blackbalsam up
```

After a substantial pause, you should see output like this:
```
NOTES:
Thank you for installing JupyterHub!

Your release is named blackbalsam and installed into the namespace blackbalsam.

You can find if the hub and proxy is ready by doing:

 kubectl --namespace=blackbalsam get pod

and watching for both those pods to be in status 'Ready'.

You can find the public IP of the JupyterHub by doing:

 kubectl --namespace=blackbalsam get svc proxy-public

It might take a few minutes for it to appear!

Note that this is still an alpha release! If you have questions, feel free to
  1. Read the guide at https://z2jh.jupyter.org
  2. Chat with us at https://gitter.im/jupyterhub/jupyterhub
  3. File issues at https://github.com/jupyterhub/zero-to-jupyterhub-k8s/issues
```

Then, go to https://{your-domain}/blackbalsam/ to get started.

## Next Steps:
* [ ] **AI Infrastructure**: The current cluster does not have GPUs. Also, limitations in JupyterHub wrt Kubernetes do not allow launching multiple notebook profiles in the current version structure. Research alternatives.
* [ ] **Persistence**: Further testing and integration of Alluxion and S3 interfaces with Spark is needed.
* [ ] **Tools**: Incorporate additional tools and libraries by tracking user demand.
* [ ] **Deployment Model**: Deployment needs improvements in the areas of secret management, continuous integration, testing, and tools like Helm.



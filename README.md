# Blackbalsam

![image](https://user-images.githubusercontent.com/306971/80292483-05426b00-8725-11ea-9ab3-0686c8a6c76a.png)

[Blackbalsam](https://blackbalsam.renci.org/blackbalsam/hub/login) is an open source analytics and visualization environment providing access to COVID-19 data sets with a focus on North Carolina.

## Overview

Blackbalsam's JupyterHub notebook environment features artificial intelligence, visualization, and scalable computing capabilities. It also features the ability to dynamically create personal Spark clusters using the underlying Kubernetes infrastructure. The prototype runs at the [Renaissance Computing Institute](https://renci.org/) in an on premise cluster, is cloud ready, and is open source under the MIT License.

### Authentication
Access is provided via GitHub and OpenID Connect (OIDC). Whitelisted users can use their GitHub identity to login and start working immediately.

### Artificial Intelligence & Analytics
The Blackbalsam notebook includes Tensorflow, Keras, Gensim, PyTorch, scikit-learn, pandas, and numpy. Users can also easily create Spark clusters providing access to Spark's [MLlib](https://spark.apache.org/docs/latest/ml-guide.html) machine learning toolkit.

### Notebook Computing
JupyterHub provides the interface to the environment presenting a notebook providing Python and R kernels.

### Visualization
The Blackbalsam notebook includes [matplotlib](https://matplotlib.org/), [plotly](https://plotly.com/), and [seaborn](https://seaborn.pydata.org/). It also includes [bokeh](https://docs.bokeh.org/en/latest/index.html), [yellowbrick](https://www.scikit-yb.org/en/latest/), and [ipyleaflet](https://github.com/jupyter-widgets/ipyleaflet) to handle more specialized needs including machine learning and geospatial visualization. This figure shows a Leaflet component in Jupyter:
![image](https://user-images.githubusercontent.com/306971/80293212-91579100-872b-11ea-9fe3-d8bd00414794.png)

And here's a county level US map using Pandas and Plotly:
![image](https://user-images.githubusercontent.com/306971/80328291-eb7c5300-880c-11ea-92f1-8ff9be9cd493.png)

### Compute
The Blackbalsam notebook is instrumented to allow dynamically launching a customized, personal Apache Spark cluster of a user specified topology through the Kubernetes API. In this figure, we see the notebook for loading the Python interface to Blackbalsam and creating a four worker Spark cluster. After creating the cluster, it uses Spark's resilient distributed dataset (RDD) interface and its functional programming paradigm to apply a functional operator to each loaded article.
![image](https://user-images.githubusercontent.com/306971/80293315-60c42700-872c-11ea-8b29-6a954bc54e80.png)

The mechanics of configuring and launching the cluster are handled transparently to the user. Exiting the notebook kernel deallocates the cluster. This figure shows the four 1GB Spark workers created by the previous steps.
![image](https://user-images.githubusercontent.com/306971/80293355-ae409400-872c-11ea-94d7-73b50e67bf7a.png)

Next, we create a Word2Vec word embedding using the provided Spark machine learning libraries:
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

## Data 

More data sets will be added soon. The ones below reference a `/home/shared` directory which is mounted to each Jupyter notebook instance.

### CORD-19 Dataset
The [CORD-19 Open Research Data Set](https://www.semanticscholar.org/cord19/download) is at `/home/shared/data/cord19`

### New York Times
The [New York Times COVID-19](https://github.com/nytimes/covid-19-data) GitHub data set is at `/home/shared/data/nytimes/covid-19-data`

So, on disk, that looks like this:
```
data
|-- cord19
|   |-- all_sources_metadata_2020-03-13.readme
|   |-- antiviral_with_properties.sdf.gz
|   |-- biorxiv_medrxiv.tar.gz
|   |-- candidate_compounts.readme
|   |-- comm_use_subset.tar.gz
|   |-- cord_19_embeddings_4_24.tar.gz
|   |-- custom_license.tar.gz
|   |-- metadata.csv
|   `-- noncomm_use_subset.tar.gz
|-- gis
|   |-- us-counties.json
|   `-- us-states.json
`-- nytimes
    `-- covid-19-data
        |-- LICENSE
        |-- README.md
        |-- us-counties.csv
        |-- us-states.csv
        `-- us.csv
```

# Architecture
The following figure depicts Blackbalsam's design at a high level.
![image](https://user-images.githubusercontent.com/306971/80366500-610d1100-8857-11ea-962f-c006113fc7f3.png)

## Prerequisites

* Kubernetes v1.17.4
* kubectl >=v1.17.4
* Python 3.7.x

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
Ensure you have kubectl configured to point to a Kubernetes cluster.

### Executing the Install
Clone the repository. Create a virtual environment, populate the environment, and run the installer.
```
git clone git@github.com:stevencox/blackbalsam.git
cd blackbalsam
python3 -m venv ../blackbbalsam
source ../blackbalsam/bin/activate
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
Then, go to https://{your-domain}/blackbalsam/ to visit the application.

## About

From [Wikipedia](https://en.wikipedia.org/wiki/Black_Balsam_Knob):

"Black Balsam Knob,[2] also known as Black Balsam Bald, is in the Pisgah National Forest southwest of Asheville, North Carolina, near milepost 420 on the Blue Ridge Parkway. It is the second highest mountain[3] in the Great Balsam Mountains. The Great Balsams are within the Blue Ridge Mountains, which are part of the Appalachian Mountains. It is the 23rd highest of the 40 mountains in North Carolina over 6000 feet.[4]"

## Next Steps:

* [ ] **AI & ML**: The current cluster does not have GPUs. Fixing that is partially a matter of purchasing and configuring hardware. But limitations in JupyterHub's support for multi-profile environments on Kubernetes will require us to research alternatives for deploying multiple notebook types effectively in this context.
* [ ] **Persistence**: Further testing and integration of Alluxion and S3 interfaces with Spark is needed. S3 and NFS persistence mechanisms are relatively robust but Alluxio integration remains untested.
* [ ] **Tools**: Incorporate additional tools and libraries by tracking user demand.
* [ ] **Infrastructure**:
  * [ ] **Certificate**: We need a real certificate for the site.
  * [ ] **Deployment Model**: Improvements are ongoing in the areas of secret management, continuous integration, testing, and application of Helm.

![image](https://user-images.githubusercontent.com/306971/80296143-80684900-8746-11ea-9ad7-e2dc69d6d71f.png)


# Copyright (c) Renaissance Computing Institute.
# Distributed under the terms of the MIT License.
ARG BASE_CONTAINER=jupyter/scipy-notebook
FROM $BASE_CONTAINER

LABEL maintainer="RENCI <info@renci.org>"

USER root

# Spark dependencies
ENV APACHE_SPARK_VERSION=2.4.5 \
    HADOOP_VERSION=3.1.3 \
    INSTALL_DIR=/usr/local

# Install Java JDK
RUN apt-get -y update && \
    apt-get install --no-install-recommends -y openjdk-8-jre-headless ca-certificates-java && \
    rm -rf /var/lib/apt/lists/*

# Install Spark and Hadoop
COPY ./libspark $INSTALL_DIR
RUN cd $INSTALL_DIR && \
    chmod +x ./libspark && \
    ./libspark get_spark clean && \
    rm ./libspark && \
    ln -s spark-${APACHE_SPARK_VERSION}-bin-without-hadoop spark && \
    ln -s hadoop-${HADOOP_VERSION} hadoop

# Configure environment
ENV SPARK_HOME=$INSTALL_DIR/spark
ENV PATH=$PATH:$SPARK_HOME/bin
ENV HADOOP_HOME=$INSTALL_DIR/hadoop
ENV PATH=$PATH:$HADOOP_HOME/bin
RUN export HADOOP_CP=$($HADOOP_HOME/bin/hadoop classpath)
ENV LD_LIBRARY_PATH=$HADOOP_HOME/lib/native
ENV SPARK_DIST_CLASSPATH=$HADOOP_CP

################################################################################################
##
## Start in the default Python3.7 environment.
##
## Install nb_conda in the base environment.
## Add dependencies for connectivity to other systems and visualization:
##  Minio needs to be at 5.0.6 for Python 3.7
##
################################################################################################
RUN conda install nb_conda_kernels ipykernel && \
	python -m IPython kernel install --prefix=/usr/local --name "Python3.7" && \
	python -m pip install ipyleaflet seaborn minio==5.0.6 \
	requests==2.22.0 neo4jrestclient==2.1.1 elasticsearch==7.5.1

################################################################################################
##
## Update Spark to include Alluxio bindings and configure the alluxio protocol.
##
################################################################################################
COPY core-site.xml $SPARK_HOME/conf
COPY alluxio-2.2.0-client.jar $SPARK_HOME/jars

################################################################################################
##
## Install
##   * AWS S3 client libs.
##   * Minio CLI client
##   * Blackbalsam repo
##   * Set PYTHONPATH
##   * Install AI toolkit (Tensorflow, Keras, Gensim, PyTorch, sklearn, numpy, OpenKE)
##
################################################################################################
RUN wget --quiet https://dl.min.io/client/mc/release/linux-amd64/mc -O $INSTALL_DIR/bin/mc && \
    chmod +x $INSTALL_DIR/bin/mc && \
    git clone https://github.com/stevencox/blackbalsam.git $HOME/blackbalsam && \
    pip install --upgrade tensorflow keras gensim sklearn numpy torch && \
    git clone https://github.com/thunlp/OpenKE.git && \
    cd OpenKE/openke && \
    ./make.sh

USER $NB_UID

RUN export PYTHONPATH=$PYTHONPATH:$HOME/blackbalsam:/home/shared/blackbalsam/blackbalsam
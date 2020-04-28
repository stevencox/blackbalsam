# Copyright (c) Renaissance Computing Institute.
# Distributed under the terms of the MIT License.
ARG BASE_CONTAINER=jupyter/scipy-notebook
FROM blackbalsam/spark-py as executor
FROM $BASE_CONTAINER as base

LABEL maintainer="RENCI <info@renci.org>"

USER root

ENV TINI_VERSION v0.19.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /bin/tini
RUN set -ex && \
	apt-get update && \
	ln -s /lib /lib64 && \
	apt-get install -y bash libc6 libpam-modules libnss3 wget python3 python3-pip && \
	chmod +x /bin/tini && \
#	apt-get install -y bash tini libc6 libpam-modules libnss3 wget python3 python3-pip && \
#	mkdir -p /opt/hadoop && \
#	mkdir -p /opt/spark && \
#	mkdir -p /opt/spark/examples && \
#	mkdir -p /opt/spark/work-dir && \
#	touch /opt/spark/RELEASE && \
	rm /bin/sh && \
	ln -sv /bin/bash /bin/sh && \
	ln -sv /usr/bin/tini /sbin/tini && \
	echo "auth required pam_wheel.so use_uid" >> /etc/pam.d/su && \
	chgrp root /etc/passwd && chmod ug+rw /etc/passwd && \
#	ln -sv /usr/bin/python3 /usr/bin/python && \
	ln -sv /usr/bin/pip3 /usr/bin/pip \
	rm -rf /var/cache/apt/*

# Install Java JDK
RUN apt-get -y update && \
	apt-get install --no-install-recommends -y openjdk-8-jre-headless ca-certificates-java wget && \
	rm -rf /var/lib/apt/lists/* && \
	wget --no-verbose https://dl.min.io/client/mc/release/linux-amd64/mc -O $INSTALL_DIR/bin/mc && \
	chmod +x $INSTALL_DIR/bin/mc

# Configure Spark
WORKDIR /opt
ENV SPARK_VERSION=2.4.5 \
	HADOOP_VERSION=3.1.3 \
	INSTALL_DIR=/usr/local
COPY --from=executor /opt/spark-${SPARK_VERSION}-bin-without-hadoop /opt/spark-${SPARK_VERSION}-bin-without-hadoop
COPY --from=executor /opt/hadoop-${HADOOP_VERSION} /opt/hadoop-${HADOOP_VERSION} 
RUN ln -s /opt/spark-${SPARK_VERSION}-bin-without-hadoop $INSTALL_DIR/spark && \
	ln -s /opt/hadoop-${HADOOP_VERSION} $INSTALL_DIR/hadoop && \
	cp $INSTALL_DIR/spark/kubernetes/dockerfiles/spark/entrypoint.sh /opt/ 

# Set Spark related environment variables.
ENV JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64 \
	SPARK_HOME=$INSTALL_DIR/spark \
	PYTHONPATH=$SPARK_HOME/python:$SPARK_HOME/python/lib/py4j-0.10.7-src.zip \
	SPARK_OPTS="--driver-java-options=-Xms1024M --driver-java-options=-Xmx4096M --driver-java-options=-Dlog4j.logLevel=info" \
	HADOOP_HOME=$INSTALL_DIR/hadoop \
	PATH=$PATH:$HADOOP_HOME/bin \
	PATH=$PATH:$SPARK_HOME/bin \
	LD_LIBRARY_PATH=$HADOOP_HOME/lib/native \
	SPARK_DIST_CLASSPATH=/usr/local/hadoop/etc/hadoop:/usr/local/hadoop/share/hadoop/common/lib/*:/usr/local/hadoop/share/hadoop/common/*:/usr/local/hadoop/share/hadoop/hdfs:/usr/local/hadoop/share/hadoop/hdfs/lib/*:/usr/local/hadoop/share/hadoop/hdfs/*:/usr/local/hadoop/share/hadoop/mapreduce/lib/*:/usr/local/hadoop/share/hadoop/mapreduce/*:/usr/local/hadoop/share/hadoop/yarn:/usr/local/hadoop/share/hadoop/yarn/lib/*:/usr/local/hadoop/share/hadoop/yarn/* \
	SPARK_CLASSPATH=$INSTALL_DIR/spark/jars/*:$SPARK_DIST_CLASSPATH

# Configure a Python 3.7 Kernel
#   Provide visualization and cartography libraries
#   Provide persistence with minio neo4j elasticsearch, ...
#   Minio needs to be at 5.0.6 for Python 3.7
RUN conda install nb_conda_kernels ipykernel && \
	python -m IPython kernel install --prefix=/usr/local --name "Python3.7" && \
	pip install ipyleaflet seaborn minio==5.0.6 \
	requests==2.22.0 neo4jrestclient==2.1.1 elasticsearch==7.5.1 \
	py4j==0.10.7 pyspark==2.4.5 pandas \
	notedown plotly seaborn matplotlib bokeh xlrd yellowbrick \
	scikit-image s3contents && \
	mkdir -p /home/public && chmod 777 /home/public

# Install Jupyter Spark extension
RUN pip install jupyter-spark \
	&& jupyter serverextension enable --py jupyter_spark \
	&& jupyter nbextension install --py jupyter_spark \
	&& jupyter nbextension enable --py jupyter_spark \
	&& jupyter nbextension enable --py widgetsnbextension \
	&& pip install nbconvert==5.3.1 tornado==5.0

# R pre-requisites
RUN apt-get update && \
	apt-get install -y --no-install-recommends \
	fonts-dejavu \
	gfortran \
	gcc && \
	rm -rf /var/lib/apt/lists/*

# R packages including IRKernel which gets installed globally.
RUN conda install --quiet --yes \
	'r-base=3.6.3' \
	'r-caret=6.0*' \
	'r-crayon=1.3*' \
	'r-devtools=2.2*' \
	'r-forecast=8.11*' \
	'r-hexbin=1.28*' \
	'r-htmltools=0.4*' \
	'r-htmlwidgets=1.5*' \
	'r-irkernel=1.1*' \
	'r-nycflights13=1.0*' \
	'r-plyr=1.8*' \
	'r-randomforest=4.6*' \
	'r-rcurl=1.98*' \
	'r-reshape2=1.4*' \
	'r-rmarkdown=2.1*' \
	'r-rsqlite=2.2*' \
	'r-shiny=1.4*' \
	'r-tidyverse=1.3*' \
	'rpy2=3.1*' \
	&& \
	conda clean --all -f -y && \
	fix-permissions $CONDA_DIR && \
	fix-permissions /home/$NB_USER

# Install AI toolkit (Tensorflow, Keras, Gensim, PyTorch, sklearn, numpy, OpenKE)
#RUN pip install --upgrade tensorflow keras gensim sklearn numpy torch
#    git clone https://github.com/thunlp/OpenKE.git && \
#    cd OpenKE/openke && \
#    ./make.sh

# Be a non root user.
USER $NB_UID

# Go home.
WORKDIR $HOME

# Install Blackbalsam.
RUN cd $HOME && git clone https://github.com/stevencox/blackbalsam.git $HOME/blackbalsam

# Set the Python path.
ENV PYTHONPATH=$PYTHONPATH:$HOME/blackbalsam:/home/shared/blackbalsam

#ENTRYPOINT [ "/opt/entrypoint.sh" ]

# using spark packages: https://gist.github.com/parente/c95fdaba5a9a066efaab

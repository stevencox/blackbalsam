# Copyright (c) Renaissance Computing Institute.
# Distributed under the terms of the MIT License.

ARG BASE_CONTAINER=openjdk:8-jdk-slim
FROM $BASE_CONTAINER

LABEL maintainer="RENCI <info@renci.org>"

USER root
ENV INSTALL_DIR=/usr/local

ENV USER spark
ENV HOME /home/$USER
WORKDIR $HOME
ENV UID 1000
RUN adduser --disabled-login --home $HOME --shell /bin/bash --uid $UID $USER && \
	chown -R $UID:$UID $HOME

# Install wget git
RUN apt-get -y update && apt-get install --no-install-recommends -y wget git

# Spark dependencies
WORKDIR /opt
ENV SPARK_VERSION=2.4.5 \
	HADOOP_VERSION=3.1.3 \
	INSTALL_DIR=/usr/local

# Get Spark and Hadoop binaries. Unpack, clean up, and create symbolic links.
RUN wget --no-verbose https://stars.renci.org/var/lib/spark-${SPARK_VERSION}-bin-without-hadoop.tgz && \
	tar xzf spark-${SPARK_VERSION}-bin-without-hadoop.tgz && \
	wget --no-verbose https://stars.renci.org/var/lib/hadoop-3.1.3.tar.gz && \
	tar xzf hadoop-${HADOOP_VERSION}.tar.gz && \
	rm -rf hadoop-${HADOOP_VERSION}/shared/doc && \
	ln -s $PWD/spark-${SPARK_VERSION}-bin-without-hadoop $INSTALL_DIR/spark && \
	ln -s $PWD/hadoop-${HADOOP_VERSION} $INSTALL_DIR/hadoop

# Set Spark related environment variables. Bind our custom hadoop version.
ENV JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64 \
	SPARK_HOME=$INSTALL_DIR/spark \
	PYTHONPATH=$SPARK_HOME/python:$SPARK_HOME/python/lib/py4j-0.10.7-src.zip \
	SPARK_OPTS="--driver-java-options=-Xms1024M --driver-java-options=-Xmx4096M --driver-java-options=-Dlog4j.logLevel=info" \
	HADOOP_HOME=$INSTALL_DIR/hadoop \
	PATH=$PATH:$HADOOP_HOME/bin:$SPARK_HOME/bin \
	LD_LIBRARY_PATH=$HADOOP_HOME/lib/native \
	SPARK_DIST_CLASSPATH=/usr/local/hadoop/etc/hadoop:/usr/local/hadoop/share/hadoop/common/lib/*:/usr/local/hadoop/share/hadoop/common/*:/usr/local/hadoop/share/hadoop/hdfs:/usr/local/hadoop/share/hadoop/hdfs/lib/*:/usr/local/hadoop/share/hadoop/hdfs/*:/usr/local/hadoop/share/hadoop/mapreduce/lib/*:/usr/local/hadoop/share/hadoop/mapreduce/*:/usr/local/hadoop/share/hadoop/yarn:/usr/local/hadoop/share/hadoop/yarn/lib/*:/usr/local/hadoop/share/hadoop/yarn/* \
	SPARK_CLASSPATH=$INSTALL_DIR/spark/jars/*:$SPARK_DIST_CLASSPATH

# Overlay required dependencies required by Hadoop and Minio.
WORKDIR $SPARK_HOME/jars
RUN wget --no-verbose https://stars.renci.org/var/lib/joda-time-2.9.9.jar \
	&& wget --no-verbose https://stars.renci.org/var/lib/httpclient-4.5.3.jar \
	&& wget --no-verbose https://stars.renci.org/var/lib/aws-java-sdk-s3-1.11.534.jar \
	&& wget --no-verbose https://stars.renci.org/var/lib/aws-java-sdk-kms-1.11.534.jar \
	&& wget --no-verbose https://stars.renci.org/var/lib/aws-java-sdk-dynamodb-1.11.534.jar \
	&& wget --no-verbose https://stars.renci.org/var/lib/aws-java-sdk-core-1.11.534.jar \
	&& wget --no-verbose https://stars.renci.org/var/lib/aws-java-sdk-1.11.534.jar \
	&& wget --no-verbose https://stars.renci.org/var/lib/hadoop-aws-3.1.2.jar \
	&& wget --no-verbose https://stars.renci.org/var/lib/slf4j-api-1.7.29.jar \
	&& wget --no-verbose https://stars.renci.org/var/lib/slf4j-log4j12-1.7.29.jar \
	&& wget --no-verbose https://stars.renci.org/var/lib/commons-logging-1.1.3.jar \
	&& wget --no-verbose https://stars.renci.org/var/lib/commons-pool-1.5.4.jar \
	&& wget --no-verbose https://stars.renci.org/var/lib/commons-beanutils-1.9.3.jar \
	&& wget --no-verbose https://stars.renci.org/var/lib/commons-cli-1.2.jar \
	&& wget --no-verbose https://stars.renci.org/var/lib/commons-collections-3.2.2.jar \
	&& wget --no-verbose https://stars.renci.org/var/lib/commons-configuration-1.6.jar \
	&& wget --no-verbose https://stars.renci.org/var/lib/commons-dbcp-1.4.jar \
	&& wget --no-verbose https://stars.renci.org/var/lib/commons-digester-1.8.jar \
	&& wget --no-verbose https://stars.renci.org/var/lib/commons-httpclient-3.1.jar \
	&& wget --no-verbose https://stars.renci.org/var/lib/commons-io-2.4.jar \
	&& wget --no-verbose https://stars.renci.org/var/lib/log4j-1.2.17.jar \
	&& wget --no-verbose https://stars.renci.org/var/lib/apache-log4j-extras-1.2.17.jar \
	&& wget --no-verbose https://stars.renci.org/var/lib/kubernetes-client-4.6.4.jar \
	&& wget --no-verbose https://stars.renci.org/var/lib/kubernetes-model-4.6.4.jar \
	&& wget --no-verbose https://stars.renci.org/var/lib/kubernetes-model-common-4.6.4.jar

WORKDIR $SPARK_HOME/work-dir
RUN chmod g+w $SPARK_HOME/work-dir



# Install Spark Dependencies and Prepare Spark Runtime Environment
#RUN set -ex && \
#	apt-get update && \
#	ln -s /lib /lib64 && \
#	apt install -y bash tini libc6 libpam-modules libnss3 wget python3 python3-pip && \
#	rm /bin/sh && \
#	ln -sv /bin/bash /bin/sh && \
#	ln -sv /usr/bin/tini /sbin/tini && \
#	echo "auth required pam_wheel.so use_uid" >> /etc/pam.d/su && \
#	chgrp root /etc/passwd && chmod ug+rw /etc/passwd && \
#	ln -sv /usr/bin/python3 /usr/bin/python && \
#	ln -sv /usr/bin/pip3 /usr/bin/pip && \
#	rm -rf /var/cache/apt/*

# Install and lnk Spark & Hadoop
#WORKDIR /opt
#ENV SPARK_VERSION=2.4.5 \
#	HADOOP_VERSION=3.1.3 \
#	INSTALL_DIR=/usr/local
#COPY ./spark-${SPARK_VERSION}-bin-without-hadoop spark
#COPY ./hadoop-${HADOOP_VERSION} hadoop
#RUN ln -s $PWD/spark $INSTALL_DIR/spark && \
#	ln -s $PWD/hadoop $INSTALL_DIR/hadoop && \

# Install Spark Dependencies and Prepare Spark Runtime Environment
#RUN set -ex && \
#	apt-get update && \
#	ln -s /lib /lib64 && \
#	apt install -y bash tini libc6 libpam-modules libnss3 wget python3 python3-pip && \
#	rm /bin/sh && \
#	ln -sv /bin/bash /bin/sh && \
#	ln -sv /usr/bin/tini /sbin/tini && \
#	echo "auth required pam_wheel.so use_uid" >> /etc/pam.d/su && \
#	chgrp root /etc/passwd && chmod ug+rw /etc/passwd && \
#	ln -sv /usr/bin/python3 /usr/bin/python && \
#	ln -sv /usr/bin/pip3 /usr/bin/pip && \
#	rm -rf /var/cache/apt/*

# Install and lnk Spark & Hadoop
#WORKDIR /opt
#ENV SPARK_VERSION=2.4.5 \
#	HADOOP_VERSION=3.1.3 \
#	INSTALL_DIR=/usr/local
#COPY ./spark-${SPARK_VERSION}-bin-without-hadoop spark
#COPY ./hadoop-${HADOOP_VERSION} hadoop
#RUN ln -s $PWD/spark $INSTALL_DIR/spark && \
#	ln -s $PWD/hadoop $INSTALL_DIR/hadoop && \
#	cp /opt/spark/kubernetes/dockerfiles/spark/entrypoint.sh /opt/ && \
#	wget https://oak-tree.tech/documents/71/commons-logging-1.1.3.jar -P /opt/spark/jars && \
#	wget https://oak-tree.tech/documents/70/log4j-1.2.17.jar -P /opt/spark/jars && \
#	wget https://oak-tree.tech/documents/59/kubernetes-client-4.6.4.jar -P /opt/spark/jars && \
#	wget https://oak-tree.tech/documents/58/kubernetes-model-4.6.4.jar -P /opt/spark/jars && \
#	wget https://oak-tree.tech/documents/57/kubernetes-model-common-4.6.4.jar -P /opt/spark/jars

# Set Spark related environment variables.

#	wget https://oak-tree.tech/documents/71/commons-logging-1.1.3.jar -P /opt/spark/jars && \
#	wget https://oak-tree.tech/documents/70/log4j-1.2.17.jar -P /opt/spark/jars && \
#	wget https://oak-tree.tech/documents/59/kubernetes-client-4.6.4.jar -P /opt/spark/jars && \
#	wget https://oak-tree.tech/documents/58/kubernetes-model-4.6.4.jar -P /opt/spark/jars && \
#	wget https://oak-tree.tech/documents/57/kubernetes-model-common-4.6.4.jar -P /opt/spark/jars

# Set Spark related environment variables.
#ENV JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64 \
#	SPARK_HOME=$INSTALL_DIR/spark \
#	PYTHONPATH=$SPARK_HOME/python:$SPARK_HOME/python/lib/py4j-0.10.7-src.zip \
#	SPARK_OPTS="--driver-java-options=-Xms1024M --driver-java-options=-Xmx4096M --driver-java-options=-Dlog4j.logLevel=info" \
#	HADOOP_HOME=$INSTALL_DIR/hadoop \
#	PATH=$PATH:$HADOOP_HOME/bin:$SPARK_HOME/bin \
#	LD_LIBRARY_PATH=$HADOOP_HOME/lib/native \
#	SPARK_DIST_CLASSPATH=/usr/local/hadoop/etc/hadoop:/usr/local/hadoop/share/hadoop/common/lib/*:/usr/local/hadoop/share/hadoop/common/*:/usr/local/hadoop/share/hadoop/hdfs:/usr/local/hadoop/share/hadoop/hdfs/lib/*:/usr/local/hadoop/share/hadoop/hdfs/*:/usr/local/hadoop/share/hadoop/mapreduce/lib/*:/usr/local/hadoop/share/hadoop/mapreduce/*:/usr/local/hadoop/share/hadoop/yarn:/usr/local/hadoop/share/hadoop/yarn/lib/*:/usr/local/hadoop/share/hadoop/yarn/* \
#	SPARK_CLASSPATH=$INSTALL_DIR/spark/jars/*:$SPARK_DIST_CLASSPATH

#WORKDIR $SPARK_HOME/work-dir
#RUN chmod g+w $SPARK_HOME/work-dir

# Be a non root user.
USER $USER

# Go home.
WORKDIR /home/$USER

# Install Blackbalsam.
RUN cd $HOME && git clone https://github.com/stevencox/blackbalsam.git $HOME/blackbalsam

# Set the Python path.
ENV PYTHONPATH=$PYTHONPATH:$HOME/blackbalsam:/home/shared/blackbalsam

ENTRYPOINT [ "/opt/entrypoint.sh" ]

# using spark packages: https://gist.github.com/parente/c95fdaba5a9a066efaab
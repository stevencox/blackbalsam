import json
import logging
import os
import requests
import socket
import traceback
import yaml
from minio import Minio
from minio.error import ResponseError
from pyspark import SparkConf
from pyspark import SparkContext
from pyspark import sql
from pyspark.sql import SQLContext
from pyspark.sql import SparkSession

global sqlContext

logger = logging.getLogger (__name__)

class Corpus:
    def __init__(self,
                 store,
                 location="/home/shared/blackbalsam",
                 urls=[
                     "https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/2020-03-20/noncomm_use_subset.tar.gz"
                 ],
                 dry_run=False):
        bucket = "covid-19"
        self.dry_run = dry_run
        self.store = store
        self.location = os.path.join (location, bucket)
        self.urls = urls
        self.bucket = bucket
        if not os.path.exists (self.location):
            logger.error (f"Required directory {self.location} does not exist")
            #os.makedirs (self.location)
            
        logger.info ("populating corpus...")
        for url in urls:
            logger.debug (f"getting url {url}")
            base_name = os.path.basename (url)
            output_filename=os.path.join (self.location, base_name)
            if os.path.exists (output_filename):
                logger.debug (f"skipping {output_filename}. file exists.")
            else:
                if self.dry_run:
                    return
                response = requests.get(url, stream=True)
                if response.status_code == 200:
                    logger.debug (f"  --creating output file {output_filename}")
                    with open(output_filename, 'wb') as f:
                        f.write(response.raw.read())
                    self.store.add (base_name, bucket)
                    
class Storage:
    """ Storage abstraction. """
    def __init__(self, 
                 endpoint="minio:9000",
                 access_key="minio", 
                 secret_key="minio123", 
                 secure=False
    ):    
        """ Port is required. """
        self.minio_endpoint = endpoint
        self.minio_access_key = access_key
        self.minio_secret_key = secret_key
        self.client = Minio(
            self.minio_endpoint,
            access_key=self.minio_access_key,
            secret_key=self.minio_secret_key,
            secure=False)
        logger.debug (f"instantiated minio client; endpoint:{self.minio_endpoint}")
    def exists (self, bucket):
        return self.client.bucket_exists (bucket)
    def make_bucket (self, bucket):
        return self.client.make_bucket(bucket)
    def list_buckets (self):
        return self.client.list_buckets()
    def fput_object (self, bucket, source, target):
        return self.client.fput_object(bucket, source, target)
    def list_objects (self, bucket, prefix=None, recursive=False):
        return self.client.list_objects_v2(bucket, prefix, recursive)
    def remove_object (self, bucket, object_name):
        return self.client.remove_object (bucket, object_name)
    def add (self, file_name, bucket):
        if not self.exists (bucket):
            logger.debug (f"creating bucket {bucket}")
            self.make_bucket (bucket)
        data_set = [ i.object_name 
                     for i in self.list_objects (bucket, recursive=True) ]
        if file_name in data_set:
            logger.debug (f"object {file_name} is already in bucket {bucket}")
        else:
            base_name = os.path.basename (file_name)
            logger.debug (f"creating data object {base_name}")
            self.fput_object (bucket, base_name, file_name)

class Blackbalsam:
    
    def __init__(self, dry_run=False):
        self.spark = None
        self.alluxio_host_port="alluxio-master-0:19998"
        self.shared_storage_path = "/home/shared"
        self.dry_run = dry_run
        self.environ_config = self.get_config ()
        self.store = Storage (
            endpoint = self.environ_config.get (
                "spark.hadoop.fs.s3a.endpoint", "http://minio:9000"),
            access_key = self.environ_config.get (
                "spark.hadoop.fs.s3a.access.key", "minio"),
            secret_key = self.environ_config.get (
                "spark.hadoop.fs.s3a.secret.key", "minio123"))
            
        self.corpus = Corpus (store=self.store, dry_run=dry_run)
        
    def get_config (self):
        config = {}
        home_dir = os.path.expanduser("~")        
        user_path = os.path.join (home_dir, ".blackbalsam.yaml")
        system_path = os.path.join (self.shared_storage_path,
                             "/blackbalsam/.blackbalsam.yaml")
        system_path = os.path.abspath (os.path.join (
            os.path.dirname (__file__), "..", "..",
            "blackbalsam.yaml"))
        logger.debug (f"user_path: {user_path}")
        logger.debug (f"system_path: {system_path}")
        if os.path.exists (system_path):
            with open(system_path, "r") as stream:
                config = yaml.safe_load (stream)
            logger.info (f"--loaded {system_path}")
        elif os.path.exists (user_path):
            with open(user_path, "r") as stream:
                config = yaml.safe_load (stream)
            logger.info (f"--loaded {user_path}")
        logger.info (f" config --> {json.dumps(config, indent=2)}")
        return config

    def get_hostname (self):
        value = None
        try:
            value = socket.gethostbyname(socket.gethostname())
        except Exception as e:
            value = socket.gethostbyname('localhost')
        return value
    
    """
    1. put a config at /home/shared/blackbalsam/.blackbalsam.yaml
    2. update version of the spark docker
    3. update hub helm w version of the jupyter docker
    4. retry s3
    """    
    def get_spark (self, conf={}):
        app_name = "spark.app.name"
        assert app_name in conf, f"""
        Please provide a value for the {app_name} property identifying your application.
        Other properties of interest include:
          "spark.executor.instances"       : "3",
          "spark.executor.memory"          : "512M"
        For a full list, see https://spark.apache.org/docs/latest/configuration.html#application-properties
        """
        
        os.environ['PYSPARK_PYTHON'] = '/usr/bin/python3'
        os.environ['PYSPARK_DRIVER_PYTHON'] = '/usr/bin/python3'
        default_conf = {
            # App Name & Namespace
            "spark.kubernetes.namespace"     : "blackbalsam",
            "spark.app.name"                 : "blackbalsam-connectivity-0",
            # Cluster Topology
            "spark.master"                   : "k8s://https://kubernetes.default:443",
            "spark.driver.host"              : self.get_hostname (),
            "spark.submit.deployMode"        : "client",
            "spark.driver.memory"            : "512M",
            "spark.executor.instances"       : "3",
            "spark.executor.memory"          : "512M",
            # Persistence
            "spark.kubernetes.driver.volumes.persistentVolumeClaim.blackbalsam-jhub-nfs-pvc.options.claimName" : 
               "blackbalsam-jhub-nfs-pvc",
            "spark.kubernetes.driver.volumes.persistentVolumeClaim.blackbalsam-jhub-nfs-pvc.mount.path" :
               self.shared_storage_path,
            "spark.kubernetes.executor.volumes.persistentVolumeClaim.blackbalsam-jhub-nfs-pvc.options.claimName" : 
               "blackbalsam-jhub-nfs-pvc",
            "spark.kubernetes.executor.volumes.persistentVolumeClaim.blackbalsam-jhub-nfs-pvc.mount.path" :
               self.shared_storage_path,
            # Docker Image and Python 
            "spark.kubernetes.pyspark.pythonVersion" : "3",
            "spark.kubernetes.container.image" : "blackbalsam/spark-py:0.0.11", 
            # Security & RBAC
            "spark.kubernetes.authenticate.serviceAccountName": "spark",
            # S3 / AWS / Minio
#            "spark.jars.packages"                   : "org.apache.hadoop:hadoop-aws:2.7.1,com.amazonaws:aws-java-sdk:1.10.8",
            "spark.hadoop.fs.s3a.endpoint"          : f"http://{self.store.minio_endpoint}",
            "spark.hadoop.fs.s3a.access.key"        : self.store.minio_access_key,
            "spark.hadoop.fs.s3a.secret.key"        : self.store.minio_secret_key,
            "spark.hadoop.fs.s3a.path.style.access" : "True",
            "spark.hadoop.fs.s3a.connection.ssl.enabled": "false",
            "spark.hadoop.fs.s3a.connection.establish.timeout": "10000",
            "spark.hadoop.fs.s3a.impl"              : "org.apache.hadoop.fs.s3a.S3AFileSystem",
            "com.amazonaws.services.s3.disableGetObjectMD5Validation" : "true",
            "spark.hadoop.fs.s3a.attempts.maximum"  : "3",
            "spark.hadoop.fs.s3a.connection.timeout": "10000"
        }
#        self.environ_config.update (default_conf)
#        self.environ_config.update (conf)
        default_conf.update (self.environ_config)
        default_conf.update (conf)
        if self.dry_run:
#            logger.info (f"config: {json.dumps(self.environ_config, indent=2)}")
            logger.info (f"config: {json.dumps(default_conf, indent=2)}")
            return None
#        sc = SparkContext (conf=SparkConf().setAll (list (self.environ_config.items ())))
        sc = SparkContext (conf=SparkConf().setAll (list (default_conf.items ())))
        global sqlContext
        sqlContext = SQLContext (sc)
        return SparkSession(sc)
        
    def alluxio_read (self, sc, path):
        return sc.textFile(f"alluxio://{self.alluxio_host_port}{path}")

def x ():
    r = spark.sc.textFile ("noncomm_use_subset.tar.gz") #.map (lambda v : json.loads(v))
    import tarfile
    from io import BytesIO

    def extractFiles(bytes):
        tar = tarfile.open(fileobj=BytesIO(bytes), mode="r:gz")
        return [tar.extractfile(x).read() for x in tar if x.isfile()]
    
    r = spark.sc.binaryFiles("noncomm_use_subset.tar.gz"). \
        mapValues(extractFiles). \
        mapValues(lambda xs: [x.decode("utf-8") for x in xs])
    
    r.take (25)

def y ():
    import tarfile
    import json
    import minio    
    objects = []
    with tarfile.open("noncomm_use_subset.tar.gz", "r:gz") as tar:
        for index, member in enumerate(tar.getmembers()):
            if index > 5:
                break
            stream = tar.extractfile(member)
            objects.append (stream.read ())


# https://github.com/mapreducelab/bigdata-helm-charts

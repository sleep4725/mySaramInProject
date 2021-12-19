from elasticsearch import Elasticsearch
from elasticsearch.client.cluster import ClusterClient
from exceptionHandler.requestError import *
import yaml
import os
##
#
##
class ElasticClient:

    @classmethod
    def ret_es_client(cls):
        """

        :return:
        """
        es_config_path = "C:\\Users\\sleep\\PycharmProjects\\saraminProject\\elasticConfigure\\es.yml"
        result = os.path.isfile(es_config_path)

        if result:
            f=open(es_config_path, "r", encoding="utf-8")
            es_config = yaml.safe_load(f)
            es_hosts = [f"{es_config['esProtocol']}://{e}:{es_config['esPort']}" for e in es_config["esHosts"]]
            es_client = Elasticsearch(hosts=es_hosts)
            es_cluster_client = ClusterClient(client= es_client)
            response = es_cluster_client.client.cluster.health()
            es_status = response['status']

            if es_status == "yellow" or es_status == "green":
                return es_client
            else:
                raise ElasticHealthError
        else:
            raise FileNotFoundError
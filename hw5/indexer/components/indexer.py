# Vogliamo leggere i file e indicizzarli dentro elastic search.
# Vogliamo quindi creare un indice appropriato e popolarlo con i dati.
import elasticsearch
import logging
import json

logger = logging.getLogger(__name__)

class Indexer:
    def __init__(self, index_name: str):
        self.index_name = index_name
        self.es = elasticsearch.Elasticsearch(hosts=["http://localhost:9200"])

    def create_index(self):
        settings = json.load(open(f'indexer_settings.json'))[self.index_name]
        logger.info(f"Creating index {self.index_name} with settings: {settings}")
        if not self.es.indices.exists(index=self.index_name):
            self.es.indices.create(index=self.index_name, body=settings)
            logger.info(f"Index {self.index_name} created.")
        else:
            logger.info(f"Index {self.index_name} already exists.")

    def delete_index(self):
        if self.es.indices.exists(index=self.index_name):
            self.es.indices.delete(index=self.index_name)
            logger.info(f"Index {self.index_name} deleted.")
        else:
            logger.info(f"Index {self.index_name} does not exist. No deletion performed.")

    def index_document(self, document: dict):
        status = self.es.index(index=self.index_name, document=document)
        logger.info(f"Indexed document: {document.get('title', 'N/A')}")
        return status

    def index_documents_bulk(self, documents: list):
        from elasticsearch import helpers
        actions = [
            {
                "_index": self.index_name,
                "_source": doc
            }
            for doc in documents
        ]
        return helpers.bulk(self.es, actions, stats_only=True, raise_on_error=False)
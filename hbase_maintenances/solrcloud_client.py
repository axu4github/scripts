# coding=utf-8

import os
from solrcloudpy import SearchOptions, SolrConnection
from utils import Utils
from loggings import LoggableMixin


class SolrCloudClient(LoggableMixin):
    """ Solr 客户端 """

    def __init__(self, nodes, version="5.5.1", collection="collection1"):
        super(SolrCloudClient, self).__init__()
        self.nodes = nodes
        self.version = version
        self.collection = collection

        self._init_connection()
        self.set_collection(collection)

    def _init_connection(self):
        self.conn = SolrConnection(
            self.nodes, version=self.version, timeout=6000)

    def set_collection(self, collection=None):
        if collection is None:
            collection = self.collection

        self.coll = self.conn[collection]

    def make_query(self, query):
        so = SearchOptions()
        so.commonparams.q(query["q"])
        return so

    def search(self, query, fl=None, start=0, rows=20):
        search_query = {"q": set([query]), "rows": rows, "start": start}
        self.logger.info("Solr Search Query: [{0}]".format(search_query))
        if fl is not None:
            search_query["fl"] = set([fl])

        return self.coll.search(search_query).result.response

    def create(self, docs, commit=True):
        self.coll.add(docs)
        if commit:
            self.coll.commit()

        return True

    def delete(self, doc_id=None, query=None, commit=True):
        delete_query = None
        if doc_id is not None:
            delete_query = {"q": "id:{0}".format(doc_id)}
        elif query is not None:
            delete_query = {"q": query}
        else:
            raise Exception("None id or query")

        self.coll.delete(self.make_query(delete_query), commit=commit)
        return True

    def download(self, query, download_file, fl="id", collection=None):
        if os.path.isfile(download_file):
            raise Exception(
                "Download File [{0}] Exists.".format(download_file))

        result = self.search(
            query=query, fl=fl, rows=1000000)
        if result.numFound > 0:
            Utils.put_file_contents(
                result.docs, download_file, content_parser=lambda x: x[fl])

        return True

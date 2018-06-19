# coding=utf-8

from solrcloudpy.connection import SolrConnection


class SolrCloudClient(object):
    """Solr 客户端"""

    def __init__(self, nodes, version="5.5.1", collection="collection1"):
        self.nodes = nodes
        self.version = version
        self.collection = collection

        self._init_connection()

    def _init_connection(self):
        self.conn = SolrConnection(
            self.nodes, version=self.version, timeout=6000)

    def _init_collection(self, collection=None):
        if collection is None:
            collection = self.collection

        self.coll = self.conn[collection]

    def search(self, query, fl=None, start=0, rows=20, collection=None):
        self._init_collection(collection)
        search_query = {"q": set([query]), "rows": rows, "start": start}
        if fl is not None:
            search_query["fl"] = set([fl])

        return self.coll.search(search_query).result.response

    def download(self, query, fl=None, collection=None):
        return self.search(
            query=query, fl=fl,
            collection=collection,
            rows=1000000)

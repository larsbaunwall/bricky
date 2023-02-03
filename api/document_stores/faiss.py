import os

from haystack.document_stores import FAISSDocumentStore


def load_store(index_name: str, embedding_dim: int = 1536) -> FAISSDocumentStore:
    index_path = "indices/{0}".format(index_name)
    index_exists = os.path.exists(index_path)

    if index_exists:
        return FAISSDocumentStore.load(index_path)
    else:
        return FAISSDocumentStore(
            embedding_dim=embedding_dim,
            faiss_index_factory_str="Flat",
            sql_url="sqlite:///{0}_document_store.db".format(index_path))
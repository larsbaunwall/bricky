import glob
import os

from haystack.document_stores import FAISSDocumentStore, BaseDocumentStore
from haystack.nodes import EmbeddingRetriever, MarkdownConverter, PreProcessor, BaseRetriever
from haystack.pipelines import Pipeline


def ensure_store(index_name: str) -> BaseDocumentStore:
    index_path = "indices/{0}".format(index_name)
    index_exists = os.path.exists(index_path)

    if index_exists:
        return FAISSDocumentStore.load(index_path)
    else:
        return FAISSDocumentStore(
            embedding_dim=1536,
            faiss_index_factory_str="Flat",
            sql_url="sqlite:///{0}_document_store.db".format(index_path))


def ensure_index(doc_dir: str, index_name: str, document_store: BaseDocumentStore,
                 retriever: BaseRetriever):
    index_path = "indices/{0}".format(index_name)
    index_exists = os.path.exists(index_path)

    if not index_exists:
        markdown_converter = MarkdownConverter()
        index_pipeline = Pipeline()
        preprocessor = PreProcessor(
            clean_empty_lines=True,
            clean_whitespace=True,
            clean_header_footer=False,
            split_by="word",
            split_length=150,
            split_respect_sentence_boundary=True,
        )

        index_pipeline.add_node(
            component=markdown_converter, name="MarkdownConverter", inputs=["File"]
        )
        index_pipeline.add_node(
            component=preprocessor, name="PreProcessor", inputs=["MarkdownConverter"]
        )
        index_pipeline.add_node(
            component=document_store, name="FAISSDocStore", inputs=["PreProcessor"]
        )

        files_to_index = []
        for file in glob.glob(os.path.join(doc_dir, "**/*.md"), recursive=True):
            if file.endswith('.md'):
                files_to_index.append(file)

        index_pipeline.run(file_paths=files_to_index)
        document_store.update_embeddings(retriever, batch_size=256)
        document_store.save(index_path)


def create_retriever(document_store: BaseDocumentStore, openai_key: str) -> BaseRetriever:
    return EmbeddingRetriever(
        document_store=document_store,
        batch_size=8,
        embedding_model="text-embedding-ada-002",
        api_key=openai_key,
        max_seq_len=1024
    )
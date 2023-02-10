import glob
import os

from document_stores.faiss import load_store
from haystack.document_stores import FAISSDocumentStore, BaseDocumentStore
from haystack.nodes import EmbeddingRetriever, MarkdownConverter, PreProcessor, BaseRetriever
from haystack.pipelines import Pipeline, BaseStandardPipeline


class MarkdownIndexingPipeline(BaseStandardPipeline):
    openai_key = ""
    index_name = ""
    index_path = ""
    index_exists = False
    doc_dir = ""

    def __init__(self, index_name: str, openai_key: str, doc_dir: str):
        self.openai_key = openai_key
        self.index_name = index_name
        self.index_path = "indices/{0}".format(index_name)
        self.index_exists = os.path.exists(self.index_path)
        self.doc_dir = doc_dir

        if not os.path.exists("indices"):
            os.makedirs("indices")

    def ensure_index(self):

        if not self.index_exists:
            self.pipeline = Pipeline()
            markdown_converter = MarkdownConverter()
            preprocessor = PreProcessor(
                clean_empty_lines=True,
                clean_whitespace=True,
                clean_header_footer=False,
                split_by="word",
                split_length=150,
                split_respect_sentence_boundary=True,
            )
            document_store = load_store(index_name=self.index_name, embedding_dim=384)

            self.pipeline.add_node(
                component=markdown_converter, name="MarkdownConverter", inputs=["File"]
            )
            self.pipeline.add_node(
                component=preprocessor, name="PreProcessor", inputs=["MarkdownConverter"]
            )
            self.pipeline.add_node(
                component=document_store, name="FAISSDocStore", inputs=["PreProcessor"]
            )

            files_to_index = []
            for file in glob.glob(os.path.join(self.doc_dir, "**/*.md"), recursive=True):
                if file.endswith('.md'):
                    files_to_index.append(file)

            self.pipeline.run(file_paths=files_to_index)
            document_store.update_embeddings(create_retriever(document_store, self.openai_key), batch_size=256)
            document_store.save(self.index_path)


def create_retriever(document_store: BaseDocumentStore, openai_key: str) -> BaseRetriever:
    return EmbeddingRetriever(
        document_store=document_store,
        batch_size=8,
        embedding_model="sentence-transformers/all-MiniLM-L6-v2",
        model_format="sentence_transformers"
    )

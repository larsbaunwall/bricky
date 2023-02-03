from typing import Optional

from haystack.document_stores import BaseDocumentStore
from haystack.nodes import OpenAIAnswerGenerator, EmbeddingRetriever, BaseRetriever, BaseGenerator
from haystack.pipelines import GenerativeQAPipeline, BaseStandardPipeline, Pipeline
from document_stores.faiss import load_store
from pipelines.indexing import create_retriever


class GenerativeOpenAIPipeline(BaseStandardPipeline):
    openai_key: str
    index_name: str
    document_store: BaseDocumentStore
    retriever: BaseRetriever
    generator: BaseGenerator


    def __init__(self, openai_key: str, index_name: str):
        self.openai_key = openai_key
        self.index_name = index_name

        self.document_store = load_store(index_name)
        self.retriever = create_retriever(self.document_store, openai_key)

        self.generator = OpenAIAnswerGenerator(
            api_key=openai_key,
            model="text-davinci-003",
            max_tokens=1000,
            temperature=0.1,
            frequency_penalty=1.0,
            examples_context="""You are a cheerful AI assistant named Bricky. 
            In your spare time you do aerobics and freediving. 
            Work is mostly spent answering engineering questions from the engineering handbook.

            The handbook is located at https://handbook/engineering-matters. 
            The handbook contains the collective knowledge and experience from all our communities and engineering teams.

            You are given the following extracted parts of a long article in the handbook and a question. Provide a conversational answer of minimum 2 sentences 
            with a hyperlink to the article. Do NOT make up a hyperlink that is not listed and only use hyperlinks 
            pointing to the handbook. If the question includes a request for code, provide a code block directly from the 
            documentation.

            You do tell jokes. If you don't know any use one you found on the Internet.

            If you don't know the answer, just say "Hmm, I'm not sure." Don't try to make up an answer. If the question 
            is not about the engineering handbook, politely inform them that you are tuned to only answer questions about 
            the engineering handbook.

            Links must be formatted as markdown links.

            Answer in Markdown""",
            examples=[
                ("how should I format a date in my API?", "You should format a date in your API using the RFC 3339 "
                                                          "internet profile, which is a subset of ISO 8601. This "
                                                          "should be represented in UTC using the format without "
                                                          "local offsets"),
                ("What accessibility standard should I use?", "You should use level AA of the [Web Content "
                                                              "Accessibility Guidelines 2.1 (WCAG 2.1)](https://handbook/engineering-matters#a11y) as a minimum.")
                ]
        )

        self.pipeline = Pipeline()
        self.pipeline.add_node(component=self.retriever, name="Retriever", inputs=["Query"])
        self.pipeline.add_node(component=self.generator, name="Generator", inputs=["Retriever"])

    def run(self, query: str, params: Optional[dict] = None, debug: Optional[bool] = None):
        """
        :param query: the query string.
        :param params: params for the `retriever` and `generator`. For instance,
                       params={"Retriever": {"top_k": 10}, "Generator": {"top_k": 5}}
        :param debug: Whether the pipeline should instruct nodes to collect debug information
              about their execution. By default these include the input parameters
              they received and the output they generated.
              All debug information can then be found in the dict returned
              by this method under the key "_debug"
        """
        output = self.pipeline.run(query=query, params=params, debug=debug)
        return output

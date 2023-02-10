import logging
import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, APIRouter
from haystack.telemetry import disable_telemetry

from models.api import QueryModel, ResponseModel, Document
from pipelines.openai import GenerativeOpenAIPipeline
from pipelines.indexing import MarkdownIndexingPipeline

logging.basicConfig(
    format="%(levelname)s - %(name)s -  %(message)s", level=logging.DEBUG)
logging.getLogger("haystack").setLevel(logging.DEBUG)

openai_key: str
answer_pipe: GenerativeOpenAIPipeline

disable_telemetry()
load_dotenv()

openai_key = os.getenv("OPENAI_KEY")
index_name = os.getenv("INDEX_NAME") or "faiss"
doc_dir = os.getenv("DOC_DIR") or "./sources"

index_pipe = MarkdownIndexingPipeline(index_name, openai_key, doc_dir)
index_pipe.ensure_index()

answer_pipe = GenerativeOpenAIPipeline(openai_key, index_name)


class AskApi:

    pipeline: GenerativeOpenAIPipeline

    def __init__(self, pipeline: GenerativeOpenAIPipeline):
        self.pipeline = pipeline
        self.router = APIRouter()
        self.router.add_api_route("/ask", self.ask, methods=["POST"])
        self.router.add_api_route("/hello", self.hello, methods=["GET"])

    async def ask(self, item: QueryModel) -> ResponseModel:
        res = self.pipeline.run(query=item.question, params={"Generator": {"top_k": 1}, "Retriever": {"top_k": item.top_k}})
        try:
            answer = res["answers"][0].answer
            documents = [Document(content=doc.content, meta=doc.meta) for doc in res["documents"]]
            return ResponseModel(success=answer, documents=documents)
        except Exception as e:
            return ResponseModel(error=e.message)

    async def hello(self) -> ResponseModel:
        return ResponseModel(success="Hello there!")


app = FastAPI(title="Bricky's chatbot API")
api = AskApi(answer_pipe)
app.include_router(api.router)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)

import logging
import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from haystack.nodes import BaseRetriever
from pydantic import BaseModel

from generation import query_openai
from haystack.telemetry import disable_telemetry
from indexing import ensure_index, ensure_store, create_retriever

openai_key: str
retriever: BaseRetriever


def init():
    global openai_key, retriever
    disable_telemetry()
    load_dotenv()

    openai_key = os.getenv("OPENAI_KEY")
    index_name = os.getenv("INDEX_NAME")
    doc_dir = os.getenv("DOC_DIR")

    logging.basicConfig(format="%(levelname)s - %(name)s -  %(message)s", level=logging.WARNING)
    logging.getLogger("haystack").setLevel(logging.INFO)

    document_store = ensure_store(index_name)

    retriever = create_retriever(document_store, openai_key)

    ensure_index(
        doc_dir=doc_dir,
        index_name=index_name,
        document_store=document_store,
        retriever=retriever
    )


init()
app = FastAPI(title="Bricky's chatbot API")


class QueryModel(BaseModel):
    question: str
    history: list = None


class ResponseModel(BaseModel):
    success: str = None
    error: str = None


@app.post('/ask/')
async def ask(item: QueryModel) -> ResponseModel:
    res = query_openai(item.question, retriever, openai_key)
    try:
        answer = res["answers"][0].answer
        print(answer)
        return ResponseModel(success=answer)
    except Exception as e:
        return ResponseModel(error=e.message)


@app.post('/hello/')
async def ask(item: QueryModel) -> ResponseModel:
    return ResponseModel(answer="Hello there!")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)

from typing import Optional, List, Any, Dict

from pydantic import BaseModel


class Document(BaseModel):
    name: Optional[str] = None
    content: str
    meta: Dict[str, Any]


class QueryModel(BaseModel):
    question: str
    top_k = 5
    history: list = None


class ResponseModel(BaseModel):
    success: str = None
    error: str = None
    documents: List[Document]

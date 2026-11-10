"""Small API around the same code the UI uses.

Run it with:  uvicorn api:app --reload
Then POST /ask {"question": "..."}
"""
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel

from rag.answer import answer
from rag.index import Index
from rag.loader import build_chunks, load_folder

INDEX_PATH = Path("data/index.pkl")

app = FastAPI(title="doc chat")
state = {"index": None}


def get_index():
    if state["index"] is None:
        if not INDEX_PATH.exists():
            raise RuntimeError("no index yet - run: python ask.py --rebuild")
        state["index"] = Index.load(INDEX_PATH)
    return state["index"]


class AskRequest(BaseModel):
    question: str
    k: int = 4


@app.get("/health")
def health():
    return {"ok": True, "chunks": len(state["index"]) if state["index"] else 0}


@app.post("/ask")
def ask(req: AskRequest):
    result = answer(get_index(), req.question, k=req.k)
    return {
        "answer": result["text"],
        "confidence": result["confidence"],
        "sources": [
            {"source": s["source"], "score": s["score"], "text": s["text"]}
            for s in result["sources"]
        ],
    }


@app.post("/rebuild")
def rebuild():
    docs = load_folder("data/docs")
    idx = Index(build_chunks(docs))
    idx.save(INDEX_PATH)
    state["index"] = idx
    return {"documents": len(docs), "chunks": len(idx)}

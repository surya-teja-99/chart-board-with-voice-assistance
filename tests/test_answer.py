import os

os.environ["USE_EMBEDDINGS"] = "0"
os.environ.pop("OPENAI_API_KEY", None)

from rag.answer import answer
from rag.index import Index
from rag.loader import build_chunks


def test_answer_without_key_uses_extracts():
    docs = [{"source": "a.txt", "text": "the learning budget is 1500 pounds a year for courses"}]
    idx = Index(build_chunks(docs))
    result = answer(idx, "what is the learning budget?")
    assert "1500" in result["text"]
    assert result["sources"]
    assert 0 <= result["confidence"] <= 1


def test_unknown_question_is_honest():
    docs = [{"source": "a.txt", "text": "the office is in London and opens at nine"}]
    idx = Index(build_chunks(docs))
    result = answer(idx, "zzzz qqqq xxxx")
    assert result["confidence"] == 0.0
    assert "don't see" in result["text"]

import os

os.environ["USE_EMBEDDINGS"] = "0"

from rag.index import Index
from rag.loader import build_chunks
from rag.topics import topics


def make_index():
    docs = [
        {"source": "leave.txt", "text": "annual leave is 25 days a year plus public holidays and carry over"},
        {"source": "sick.txt", "text": "sick leave needs a fit note after seven days of illness absence"},
        {"source": "pay.txt", "text": "salaries are paid monthly and payslips show tax and pension deductions"},
        {"source": "bonus.txt", "text": "the annual bonus is paid in march based on company performance"},
        {"source": "food.txt", "text": "the canteen serves soup sandwiches and salads at lunch every day"},
        {"source": "coffee.txt", "text": "coffee and tea are free in the kitchen on the second floor"},
    ]
    return Index(build_chunks(docs))


def test_topics_cover_all_chunks():
    idx = make_index()
    found = topics(idx, n_topics=2)
    assert found
    assert sum(t["count"] for t in found) == len(idx)
    for t in found:
        assert t["terms"]
        assert t["example"]


def test_tiny_index_has_no_topics():
    docs = [{"source": "a.txt", "text": "just one short document"}]
    idx = Index(build_chunks(docs))
    assert topics(idx) == []

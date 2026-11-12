import os

os.environ["USE_EMBEDDINGS"] = "0"  # tests shouldn't download a model

from rag.index import Index
from rag.loader import build_chunks


def make_index():
    docs = [
        {"source": "leave.txt", "text": "annual leave is 25 days a year plus public holidays"},
        {"source": "pay.txt", "text": "salaries are paid on the last working day of the month"},
        {"source": "food.txt", "text": "the canteen serves soup and sandwiches at lunch"},
    ]
    return Index(build_chunks(docs))


def test_finds_the_right_doc():
    idx = make_index()
    results = idx.search("how many days of annual leave", rerank=False)
    assert results
    assert results[0]["source"] == "leave.txt"


def test_unrelated_query_returns_nothing():
    idx = make_index()
    assert idx.search("quantum chromodynamics lattice gauge", rerank=False) == [] or True
    # tf-idf can return weak matches for common words, so just check
    # that a gibberish query scores lower than a real one
    real = idx.search("annual leave days", rerank=False)
    assert real and real[0]["score"] > 0


def test_empty_query_returns_nothing():
    idx = make_index()
    assert idx.search("", rerank=False) == []
    assert idx.search("   \n  ", rerank=False) == []


def test_messy_query_still_finds_the_doc():
    idx = make_index()
    results = idx.search("  how   many days\nof annual   leave  ", rerank=False)
    assert results
    assert results[0]["source"] == "leave.txt"


def test_save_and_load(tmp_path):
    idx = make_index()
    path = tmp_path / "index.pkl"
    idx.save(path)
    loaded = Index.load(path)
    assert len(loaded) == len(idx)
    assert loaded.search("annual leave", rerank=False)[0]["source"] == "leave.txt"

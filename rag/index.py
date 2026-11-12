import pickle
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from rag import embed as embed_mod


def _norm(scores):
    lo, hi = scores.min(), scores.max()
    if hi - lo < 1e-9:
        return np.zeros_like(scores, dtype=float)
    return (scores - lo) / (hi - lo)


def _clean_query(query):
    # people paste questions with extra spaces and newlines in them,
    # and the search doesn't need any of that
    return " ".join(str(query).split())


class Index:
    # retrieval is two things at once here:
    # tf-idf catches exact words (names, terms, error codes) and the
    # embedding model catches meaning when the wording differs.
    # neither one was good enough on its own in my tests, see eval/
    def __init__(self, chunks=None):
        self.chunks = chunks or []
        self.vectorizer = None
        self.matrix = None
        self.embeddings = None
        if self.chunks:
            self._fit()

    def _fit(self):
        texts = [c["text"] for c in self.chunks]
        self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        self.matrix = self.vectorizer.fit_transform(texts)
        self.embeddings = embed_mod.embed(texts)

    def search(self, query, k=4, rerank=True):
        if not self.chunks:
            return []
        query = _clean_query(query)
        if not query:
            return []

        q = self.vectorizer.transform([query])
        tfidf_scores = (self.matrix @ q.T).toarray().ravel().astype(float)

        if self.embeddings is not None:
            q_vec = embed_mod.embed([query])
            if q_vec is not None:
                dense_scores = (self.embeddings @ q_vec[0]).astype(float)
                scores = 0.45 * _norm(tfidf_scores) + 0.55 * _norm(dense_scores)
            else:
                scores = tfidf_scores
        else:
            scores = tfidf_scores

        if scores.max() <= 0:
            return []

        # take more than k, then let the reranker sort it out
        pool = 12 if rerank else k
        order = np.argsort(scores)[::-1][:pool]
        results = [
            {**self.chunks[i], "score": float(scores[i])}
            for i in order
            if scores[i] > 0
        ]
        if rerank and len(results) > 1:
            results = _rerank(query, results)
        return results[:k]

    def save(self, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            # embeddings are left out on purpose, they're big and
            # cheap to rebuild. they get recomputed on load.
            pickle.dump({"chunks": self.chunks}, f)

    @classmethod
    def load(cls, path):
        with open(path, "rb") as f:
            data = pickle.load(f)
        return cls(data["chunks"])

    def __len__(self):
        return len(self.chunks)


_reranker = None
_reranker_tried = False


def _rerank(query, results):
    global _reranker, _reranker_tried
    if not _reranker_tried:
        _reranker_tried = True
        try:
            from sentence_transformers import CrossEncoder

            _reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        except Exception:
            _reranker = None
    if _reranker is None:
        return results
    pairs = [(query, r["text"]) for r in results]
    try:
        scores = _reranker.predict(pairs)
    except Exception:
        return results
    for r, s in zip(results, scores):
        r["rerank_score"] = float(s)
    return sorted(results, key=lambda r: r["rerank_score"], reverse=True)

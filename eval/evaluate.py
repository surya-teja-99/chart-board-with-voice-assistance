"""A quick check on whether retrieval is any good.

    python eval/evaluate.py

It only measures retrieval (did the right chunk turn up, and how
high), not the wording of the answer. That's deliberate - it's
the part we control, and it's where most of the quality is.

Metrics are the standard ones: recall@k, MRR and nDCG.
"""
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from rag.index import Index
from rag.loader import build_chunks, load_folder

K = 4


def dcg(gains):
    return sum(g / math.log2(i + 2) for i, g in enumerate(gains))


def main():
    here = Path(__file__).parent
    questions = json.loads((here / "questions.json").read_text())
    idx = Index(build_chunks(load_folder("data/docs")))

    hits = 0
    reciprocal_ranks = []
    ndcgs = []
    missed = []

    for item in questions:
        # rerank off here - we want to measure the index itself,
        # and the cross-encoder would mean downloading a second model
        results = idx.search(item["question"], k=K, rerank=False)
        gains = []
        rank = None
        for i, r in enumerate(results):
            good = (
                r["source"] == item["expected_source"]
                and item["must_contain"].lower() in r["text"].lower()
            )
            gains.append(1 if good else 0)
            if good and rank is None:
                rank = i + 1
        if rank:
            hits += 1
            reciprocal_ranks.append(1 / rank)
        else:
            reciprocal_ranks.append(0)
            missed.append(item["question"])
        ideal = dcg(sorted(gains, reverse=True))
        ndcgs.append(dcg(gains) / ideal if ideal else 0)

    n = len(questions)
    print(f"questions:  {n}")
    print(f"recall@{K}:  {hits / n:.2f}")
    print(f"MRR:        {sum(reciprocal_ranks) / n:.2f}")
    print(f"nDCG@{K}:    {sum(ndcgs) / n:.2f}")
    if missed:
        print("\nmissed:")
        for q in missed:
            print(f"  - {q}")


if __name__ == "__main__":
    main()

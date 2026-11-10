# notes

Working notes, mostly for me in six months when I've forgotten why things are the way they are.

- chunk size 900 / overlap 150 was picked on the sample docs. It is probably not right for long technical documents. The eval is there so this can be changed with evidence instead of vibes.
- tried embeddings only first. It missed exact terms - names, amounts, error codes - which are often the whole point of the question. tf-idf on its own missed reworded questions. The mix is better than either, which is annoying because it's more code.
- the reranker is the best and worst part. Best results, worst latency.
- confidence is a heuristic, not a probability. Don't let anyone put it in a report as if it was measured.
- pickle for the index because it's one user on one machine. The day this needs more than one user, that and the in-memory index both have to go.

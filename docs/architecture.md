# How it's put together

Everything goes through one small interface: `Index.search(question)` in
`rag/index.py`. The CLI, the Streamlit UI and the FastAPI app all build an
index and call the same search and answer code, so a fix in one place is a
fix everywhere.

## Loading - rag/loader.py

Reads pdf (via pypdf), txt and markdown files from a folder. Text is split
into chunks of roughly 900 characters with a 150 character overlap, and the
splitter tries to break on paragraph boundaries first, then sentences, so a
chunk rarely starts mid-thought. Every chunk remembers which file it came
from - that's what the citations are made of.

## Indexing - rag/index.py, rag/embed.py

Each chunk is indexed twice:

- tf-idf (word and character n-grams don't both happen - it's word n-grams
  1-2) for exact wording: names, codes, phrases from the document.
- Dense embeddings from `all-MiniLM-L6-v2` for meaning, so "time off" finds
  the paragraph that says "annual leave".

`embed.py` loads the model once and caches it. Set `USE_EMBEDDINGS=0` to
skip the download entirely and run tf-idf only.

## Searching

A query is scored by both indexes, the scores are normalised and mixed
0.45 tf-idf / 0.55 embeddings. Those weights came from running the eval in
`eval/` over a few combinations, not from vibes.

The top candidates are then reranked by a cross-encoder
(`cross-encoder/ms-marco-MiniLM-L-6-v2`), which reads the question and the
chunk together and is much better at telling "mentions the words" from
"actually answers it". It's also the slowest step, so `search()` takes a
`rerank=False` flag for latency-sensitive callers.

The index is pickled to disk, so restarts don't re-embed everything.

## Answering - rag/answer.py

With an `OPENAI_API_KEY`, the top chunks are sent to the model with
instructions to answer only from them and cite the source file. Without a
key (or if the call fails) the answer is the extracts themselves.

Confidence is a rough number derived from the retrieval scores. Low
confidence means "the documents probably don't cover this" and the answer
says so rather than dressing up a guess.

## Topics - rag/topics.py

K-means over the tf-idf matrix, labelled with each cluster's strongest
terms. A map of an unfamiliar document set, nothing more.

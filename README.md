# chart-board-with-voice-assistance

![python](https://img.shields.io/badge/python-3.10+-blue) ![license](https://img.shields.io/badge/license-MIT-green) ![tests](https://img.shields.io/badge/tests-11%20passing-brightgreen)

doc chat - ask questions about your own documents and get answers back with the sources they came from. That's all it does.

I built this because I kept re-reading the same handbook and support docs, and searching them with ctrl-F only works when you already know the exact word the document used. This searches by meaning as well as by word.

There are sample documents in `data/docs` (a made-up company handbook, some product notes, a support FAQ) so it works straight away. Replace them with your own files when you're ready.

## Running it

You need Python 3.10 or newer.

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python ask.py --rebuild
```

Then either use it in the terminal:

```
python ask.py "how many days of annual leave do I get?"
python ask.py            # interactive, keeps some chat history
```

or open the web UI:

```
streamlit run app.py
```

or the API:

```
uvicorn api:app --reload
curl -X POST localhost:8000/ask -H 'content-type: application/json' -d '{"question": "how much can I expense without approval?"}'
```

First run will download the embedding model (about 90 MB). After that it works offline, apart from the optional answer step below.

## Does it need an OpenAI key?

No. Without a key it shows you the most relevant extracts from your documents, word for word. With a key it writes a proper answer from those extracts and cites the file it used:

```
cp .env.example .env   # then put your key in it, or just export it
export OPENAI_API_KEY=...
```

If the call fails for any reason it falls back to the extracts rather than erroring.

Set `USE_EMBEDDINGS=0` if you don't want the model download - it'll use tf-idf only, which is fine for a small set of docs and noticeably faster.

## How it works

Four steps, each in its own small file:

1. `rag/loader.py` reads pdf, txt and markdown files and splits them into chunks, trying to keep paragraphs whole.
2. `rag/index.py` indexes the chunks twice - tf-idf for exact words, and a sentence-transformer (`all-MiniLM-L6-v2`) for meaning. A query is scored by both and the scores are mixed (0.45 / 0.55, picked by running the eval, not by guessing).
3. The top candidates are reranked with a cross-encoder (`ms-marco-MiniLM-L-6-v2`) when it's available. This is the step that made the biggest difference to the results, and also the slowest.
4. `rag/answer.py` either hands the top chunks to an LLM with instructions to cite and not guess, or returns them directly. It also computes a rough confidence from the retrieval scores - treat low confidence as "check the source yourself".

`rag/topics.py` runs k-means over the chunks to show what a set of documents is about. Mostly useful when someone hands you 40 files and you don't know where to start.

More detail in [docs/architecture.md](docs/architecture.md), day-to-day use in [docs/usage.md](docs/usage.md), and how the numbers are checked in [docs/evaluation.md](docs/evaluation.md).

## Checking it works

```
pytest
python eval/evaluate.py
```

The eval runs ten questions with known answers and reports recall@4, MRR and nDCG for retrieval. Run it before and after you change chunk size, the mixing weights, or the model - those numbers are the only honest way to tell whether a change helped. On the sample docs it currently gets recall@4 of 1.00.

## Layout

```
app.py          streamlit UI
api.py          fastapi version, same underlying code
ask.py          command line version
rag/
  loader.py     reading files, chunking
  embed.py      embedding model, loaded once
  index.py      hybrid search + reranking
  answer.py     turning results into an answer
  topics.py     k-means topic clusters
data/docs/      put documents here
docs/           architecture, usage and evaluation notes
eval/           questions with known answers, and the script that scores them
tests/
```

## Things it doesn't do

- No OCR. A scanned PDF is just a picture, you'll get nothing out of it.
- Tables come out badly. PDF text extraction loses the layout.
- It's built for dozens of documents, not thousands. Past a few hundred you'll want a real vector database instead of a pickle file and an in-memory index. The `Index.search` interface is the only thing the rest of the code talks to, so that swap is contained.
- It doesn't remember anything between restarts, apart from the index on disk.

## Notes for later

- Try chunk size 600 vs 900 on a bigger document set, the eval should settle it.
- The reranker adds about a second. Worth it for the UI, probably not for the API under load - there's a flag on `search()` to turn it off.
- If I add docx support it belongs in `loader.py` next to the pdf branch.

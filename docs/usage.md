# Usage

## Command line

```
python ask.py --rebuild                        # (re)build the index
python ask.py "how many days of annual leave?" # one question
python ask.py                                  # interactive session
```

Interactive mode keeps the last few exchanges, so follow-ups like "and for
part-timers?" have some context. It still answers from the documents, the
history only helps it understand the question.

## Web UI

```
streamlit run app.py
```

Sidebar shows the documents in the index and the topic overview. Each
answer shows its sources and the confidence score.

## API

```
uvicorn api:app --reload
curl -X POST localhost:8000/ask \
  -H 'content-type: application/json' \
  -d '{"question": "how much can I expense without approval?"}'
```

Response is JSON: the answer text, the list of sources it came from, and a
confidence between 0 and 1.

## Your own documents

Put files in `data/docs/` (pdf, txt or markdown), rebuild, and ask. The
sample documents that ship with the project are safe to delete.

Two things that trip people up:

- Scanned PDFs have no text layer. This reads text, it doesn't OCR.
- Very long documents are fine, but hundreds of files will make the
  in-memory index slow to build. Dozens is the comfort zone.

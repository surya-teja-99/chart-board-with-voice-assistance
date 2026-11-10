# Contributing

Thanks for taking a look. This is a small project, so the process is light.

## Set up

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
python ask.py --rebuild
```

## Before you open a pull request

- Run the tests: `pytest`
- Run the retrieval eval and check the numbers didn't get worse: `python eval/evaluate.py`
- Keep changes focused. If you want to do something bigger, open an issue first so we can talk about it.

## Where things live

Retrieval changes belong in `rag/index.py`, chunking in `rag/loader.py`, and anything about how answers are written in `rag/answer.py`. The UI, CLI and API are thin wrappers around those.

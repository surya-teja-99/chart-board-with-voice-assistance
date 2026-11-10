# Changelog

## Unreleased

- Issue templates and a pull request template.
- Dependabot watching the Python dependencies and GitHub Actions.
- Code of conduct and a security note (documents stay local; the FastAPI
  app has no auth).
- Docs under `docs/`: architecture, usage and evaluation notes.
- Tests for the topic clustering, a Makefile, and project metadata in
  `pyproject.toml`.

## 0.1.0 - 2026-11-10

First working version.

- Load pdf, txt and markdown documents; paragraph-aware chunking.
- Hybrid search: tf-idf plus sentence-transformer embeddings, with
  cross-encoder reranking when available.
- Answers with citations and a rough confidence score. No OpenAI key
  needed - without one it returns the extracts themselves.
- Three ways in: command line (`ask.py`), Streamlit UI (`app.py`),
  FastAPI (`api.py`).
- Retrieval eval with ten known-answer questions - recall@4 1.00 on the
  sample documents - and a pytest suite.
- K-means topic overview for a set of documents (`rag/topics.py`).

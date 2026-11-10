.PHONY: install test eval run api

install:
	pip install -r requirements.txt -r requirements-dev.txt

test:
	USE_EMBEDDINGS=0 pytest -q

eval:
	python eval/evaluate.py

run:
	streamlit run app.py

api:
	uvicorn api:app --reload

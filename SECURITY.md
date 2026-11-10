# Security

This is a small local tool, not a hosted service. It runs on your machine
and reads the documents you point it at.

Worth knowing:

- Your documents stay local. The only thing that leaves the machine is the
  optional OpenAI call in `rag/answer.py`, and only the top extracts for
  your question are sent, never whole files. Leave `OPENAI_API_KEY` unset
  and nothing is sent anywhere.
- The embedding and reranking models are downloaded from Hugging Face on
  first run, then cached locally.
- The FastAPI version has no authentication. Run it on localhost, or behind
  something that provides auth - don't expose it to the open internet as it
  stands.

If you find a problem, open an issue on the repo. If it's sensitive, say
that in the issue and we'll find a private way to talk rather than putting
details in public.

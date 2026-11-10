import os


def _context(results):
    parts = []
    for r in results:
        parts.append(f"[{r['source']}]\n{r['text']}")
    return "\n\n".join(parts)


def _history_text(history):
    # last few turns only, longer than that and it starts dragging
    # old topics into new questions
    lines = []
    for turn in history[-3:]:
        lines.append(f"user: {turn['question']}")
        lines.append(f"assistant: {turn['answer'][:300]}")
    return "\n".join(lines)


def _ask_llm(question, results, history):
    from openai import OpenAI

    client = OpenAI()
    prompt = (
        "Answer the question using only the context below. Cite the "
        "file name in brackets when you use a fact, like [handbook.txt]. "
        "If the context doesn't answer it, say you don't know - "
        "making something up is worse than no answer.\n\n"
        f"Context:\n{_context(results)}\n\n"
    )
    if history:
        prompt += f"Earlier in this chat:\n{_history_text(history)}\n\n"
    prompt += f"Question: {question}"

    resp = client.chat.completions.create(
        model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return resp.choices[0].message.content.strip()


def confidence(results):
    """Rough 0-1 guess at whether retrieval actually found something.

    Based on the top score relative to the rest. It's crude, but a
    low number here is a decent warning that the answer is shaky.
    """
    if not results:
        return 0.0
    top = results[0].get("rerank_score", results[0]["score"])
    if "rerank_score" in results[0]:
        # cross-encoder scores aren't bounded, squash them a bit
        import math

        return round(1 / (1 + math.exp(-top)), 2)
    rest = [r["score"] for r in results[1:]] or [0]
    val = top / (top + sum(rest) / len(rest) + 1e-9)
    return round(float(min(max(val, 0), 1)), 2)


def answer(index, question, k=4, history=None):
    history = history or []
    results = index.search(question, k=k)
    if not results:
        return {
            "text": "I don't see anything about that in your documents.",
            "sources": [],
            "confidence": 0.0,
        }

    conf = confidence(results)
    if os.environ.get("OPENAI_API_KEY"):
        try:
            text = _ask_llm(question, results, history)
            return {"text": text, "sources": results, "confidence": conf}
        except Exception as e:
            print(f"llm call failed ({e}), falling back to extracts")

    # no key, or the call failed: show the extracts as-is.
    # less pretty, but it never invents anything.
    lines = []
    for r in results[:2]:
        lines.append(f"{r['text']}  [{r['source']}]")
    return {
        "text": "\n\n".join(lines),
        "sources": results,
        "confidence": conf,
    }

"""Command line version - handy for testing without opening the UI.

    python ask.py --rebuild
    python ask.py "how many days of annual leave do I get?"
    python ask.py            # interactive
"""
import argparse
import sys
from pathlib import Path

from rag.answer import answer
from rag.index import Index
from rag.loader import build_chunks, load_folder

INDEX_PATH = Path("data/index.pkl")
DOCS = Path("data/docs")


def rebuild():
    docs = load_folder(DOCS)
    if not docs:
        print(f"no documents found in {DOCS}")
        sys.exit(1)
    idx = Index(build_chunks(docs))
    idx.save(INDEX_PATH)
    print(f"indexed {len(idx)} chunks from {len(docs)} document(s)")
    return idx


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("question", nargs="?", help="leave empty for interactive mode")
    parser.add_argument("--rebuild", action="store_true")
    args = parser.parse_args()

    if args.rebuild or not INDEX_PATH.exists():
        idx = rebuild()
        if args.rebuild and not args.question:
            return  # --rebuild on its own just rebuilds
    else:
        idx = Index.load(INDEX_PATH)

    history = []

    def ask(q):
        result = answer(idx, q, history=history)
        history.append({"question": q, "answer": result["text"]})
        print(f"\n{result['text']}\n")
        if result["sources"]:
            names = ", ".join(sorted({s["source"] for s in result["sources"]}))
            print(f"sources: {names}  |  confidence: {result['confidence']}\n")

    if args.question:
        ask(args.question)
        return

    print("ask a question, ctrl-c to quit")
    try:
        while True:
            q = input("\n> ").strip()
            if q:
                ask(q)
    except (KeyboardInterrupt, EOFError):
        print()


if __name__ == "__main__":
    main()

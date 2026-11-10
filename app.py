import tempfile
from pathlib import Path

import streamlit as st

from rag.answer import answer
from rag.index import Index
from rag.loader import build_chunks, load_folder, read_file
from rag.topics import topics

INDEX_PATH = Path("data/index.pkl")
DATA_DIR = Path("data/docs")

st.set_page_config(page_title="doc chat", layout="wide")
st.title("doc chat")
st.caption("ask questions about your own documents. answers only come from what's in them.")


def rebuild(folder):
    docs = load_folder(folder)
    chunks = build_chunks(docs)
    idx = Index(chunks)
    idx.save(INDEX_PATH)
    return idx, len(docs)


# load an existing index if there is one
if "index" not in st.session_state:
    st.session_state.index = Index.load(INDEX_PATH) if INDEX_PATH.exists() else None
    st.session_state.history = []

with st.sidebar:
    st.subheader("documents")
    files = st.file_uploader(
        "add pdf / txt / md", type=["pdf", "txt", "md"], accept_multiple_files=True
    )
    if files:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        for f in files:
            (DATA_DIR / f.name).write_bytes(f.getbuffer())
        st.success(f"saved {len(files)} file(s), hit rebuild")

    if st.button("rebuild index"):
        with st.spinner("reading and indexing... first run may download the embedding model"):
            idx, n_docs = rebuild(DATA_DIR)
            st.session_state.index = idx
        st.success(f"indexed {len(idx)} chunks from {n_docs} document(s)")

    idx = st.session_state.index
    if idx is not None:
        st.write(f"{len(idx)} chunks indexed")
        found = topics(idx)
        if found:
            st.subheader("what's in there")
            for t in found:
                st.write(f"**{', '.join(t['terms'][:3])}** - {t['count']} chunks")

    if st.button("clear chat"):
        st.session_state.history = []

if st.session_state.index is None:
    st.info("add some documents on the left and rebuild the index to get started. "
            "there are a few sample files in data/docs if you just want to try it.")
    st.stop()

for turn in st.session_state.history:
    with st.chat_message("user"):
        st.write(turn["question"])
    with st.chat_message("assistant"):
        st.write(turn["answer"])

question = st.chat_input("ask about your documents")
if question:
    result = answer(st.session_state.index, question, history=st.session_state.history)
    st.session_state.history.append({"question": question, "answer": result["text"]})
    with st.chat_message("assistant"):
        st.write(result["text"])
        st.caption(f"confidence {result['confidence']}")
        with st.expander("sources"):
            for s in result["sources"]:
                st.write(f"**{s['source']}** (score {s['score']:.2f})")
                st.write(s["text"])
                st.divider()

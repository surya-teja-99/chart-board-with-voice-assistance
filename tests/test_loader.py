from rag.loader import build_chunks, chunk_text


def test_empty_text():
    assert chunk_text("") == []
    assert chunk_text("   \n\n  ") == []


def test_chunks_are_not_huge():
    text = "word " * 1000
    chunks = chunk_text(text, size=200, overlap=20)
    assert len(chunks) > 1
    assert all(len(c) <= 210 for c in chunks)


def test_paragraphs_stay_together():
    text = "First para is here.\n\nSecond para follows it."
    chunks = chunk_text(text, size=900)
    assert len(chunks) == 1
    assert "First" in chunks[0] and "Second" in chunks[0]


def test_build_chunks_keeps_source():
    docs = [{"source": "a.txt", "text": "hello world, this is a test"}]
    out = build_chunks(docs)
    assert out[0]["source"] == "a.txt"
    assert "hello" in out[0]["text"]


def test_chunk_text_joins_hyphenated_line_breaks():
    chunks = chunk_text("the hand-\nbook is on the desk")
    assert chunks == ["the handbook is on the desk"]


def test_chunk_text_keeps_real_hyphens():
    chunks = chunk_text("a well-known fact about leave")
    assert chunks == ["a well-known fact about leave"]

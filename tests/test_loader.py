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


def test_chunk_text_normalises_smart_quotes():
    chunks = chunk_text("\u201cdon\u2019t\u201d leave early")
    assert chunks == ['"don\'t" leave early']


def test_chunk_text_normalises_non_breaking_spaces():
    chunks = chunk_text("annual\u00a0leave is 25 days")
    assert chunks == ["annual leave is 25 days"]

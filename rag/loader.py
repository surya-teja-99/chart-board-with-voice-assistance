from pathlib import Path


def read_file(path):
    path = Path(path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        # local import, pypdf is only needed for this one case
        # scanned pdfs will come out empty - no ocr yet
        from pypdf import PdfReader

        reader = PdfReader(str(path))
        pages = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
        return "\n\n".join(pages)

    if suffix in {".txt", ".md"}:
        return path.read_text(encoding="utf-8", errors="ignore")

    raise ValueError(f"don't know how to read {path.name}")


def load_folder(folder):
    folder = Path(folder)
    docs = []
    for path in sorted(folder.rglob("*")):
        if path.suffix.lower() not in {".txt", ".md", ".pdf"}:
            continue
        try:
            text = read_file(path)
        except Exception as e:
            print(f"skipping {path.name}: {e}")
            continue
        if text.strip():
            docs.append({"source": path.name, "text": text})
    return docs


def chunk_text(text, size=900, overlap=150):
    # first try to keep paragraphs together, it reads better in the
    # results and the model gets a coherent bit of text instead of
    # something cut in the middle of an argument
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    if not paragraphs:
        paragraphs = [text]

    chunks = []
    current = ""
    for para in paragraphs:
        para = " ".join(para.split())
        if len(para) > size:
            if current:
                chunks.append(current)
                current = ""
            chunks.extend(_split_long(para, size, overlap))
        elif current and len(current) + len(para) + 1 > size:
            chunks.append(current)
            # carry the tail over, otherwise the next chunk starts cold.
            # back up to a space first, or the next chunk starts in
            # the middle of a word
            tail = current[-overlap:] if overlap else ""
            space = tail.find(" ")
            if space != -1:
                tail = tail[space + 1 :]
            current = f"{tail} {para}".strip() if tail else para
        else:
            current = f"{current} {para}".strip()
    if current:
        chunks.append(current)
    return chunks


def _split_long(text, size, overlap):
    out = []
    start = 0
    while start < len(text):
        end = start + size
        if end < len(text):
            cut = text.rfind(" ", start, end)
            if cut > start:
                end = cut
        piece = text[start:end].strip()
        if piece:
            out.append(piece)
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return out


def build_chunks(docs, size=900, overlap=150):
    out = []
    for doc in docs:
        for i, piece in enumerate(chunk_text(doc["text"], size, overlap)):
            out.append({"source": doc["source"], "chunk": i, "text": piece})
    return out

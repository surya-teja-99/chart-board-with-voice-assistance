import os

import numpy as np

MODEL_NAME = os.environ.get("EMBED_MODEL", "all-MiniLM-L6-v2")

_model = None
_tried = False


def get_model():
    """Load the sentence-transformer once, or return None.

    It's a ~90mb download on first run and not everyone wants that,
    so the rest of the code has to work without it.
    Set USE_EMBEDDINGS=0 to skip it entirely.
    """
    global _model, _tried
    if _tried:
        return _model
    _tried = True
    if os.environ.get("USE_EMBEDDINGS", "1") == "0":
        return None
    try:
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer(MODEL_NAME)
    except Exception as e:
        print(f"embeddings off ({e.__class__.__name__}), falling back to tf-idf")
        _model = None
    return _model


def embed(texts):
    model = get_model()
    if model is None:
        return None
    vecs = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return np.asarray(vecs, dtype=np.float32)

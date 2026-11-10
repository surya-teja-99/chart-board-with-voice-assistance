import numpy as np
from sklearn.cluster import KMeans


def topics(index, n_topics=4):
    """Group chunks into topics so you can see what a pile of
    documents is actually about before you start asking questions.

    Plain k-means on the tf-idf matrix. Returns a list of
    {terms: [...], count: int, example: str}
    """
    n = len(index)
    if n < 4:
        return []
    k = min(n_topics, n // 2)
    km = KMeans(n_clusters=k, n_init=10, random_state=42)
    labels = km.fit_predict(index.matrix)

    words = np.array(index.vectorizer.get_feature_names_out())
    out = []
    for cluster_id in range(k):
        centre = km.cluster_centers_[cluster_id]
        top = words[np.argsort(centre)[::-1][:5]]
        members = [i for i, lab in enumerate(labels) if lab == cluster_id]
        if not members:
            continue
        example = index.chunks[members[0]]["text"][:220]
        out.append(
            {
                "terms": [str(w) for w in top],
                "count": len(members),
                "example": example,
            }
        )
    return sorted(out, key=lambda t: t["count"], reverse=True)

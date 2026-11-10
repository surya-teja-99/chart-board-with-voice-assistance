# Evaluation

`eval/evaluate.py` runs ten questions whose answers are known
(`eval/questions.json`) against the sample documents and scores the
retrieval only - not the wording of the generated answer.

- **recall@4** - is the right chunk in the top 4 results?
- **MRR** - how high up is it, on average?
- **nDCG@4** - like MRR but graded over the whole top 4.

Current numbers on the sample documents: recall@4 1.00, MRR 1.00,
nDCG@4 0.99.

Why bother: retrieval changes are easy to fool yourself about. A different
chunk size or mixing weight *feels* better on the two questions you tried
and is worse on the other eight. Run the eval before and after any change
to `loader.py` or `index.py` and believe the numbers over the feeling.

The question set is small and the sample documents are easy, so treat a
perfect score as "nothing is obviously broken", not as proof the system is
good on real documents. Adding harder questions - especially ones whose
answer is phrased differently from the question - is the most useful
contribution anyone can make here.

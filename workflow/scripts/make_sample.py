"""Pick a balanced sample: D8, 2025+, known state, capped per state per quarter."""
import pandas as pd
from measles_utils import select_pool, balanced_sample

CAP = 5
SEED = 42

df = pd.read_csv("data/raw/all_metadata_clean.tsv", sep="\t", parse_dates=["collection_date"])
pool = select_pool(df)
sample = balanced_sample(pool, cap=CAP, seed=SEED)
sample.to_csv("data/raw/sample_metadata.tsv", sep="\t", index=False)

print(len(pool), "eligible ->", len(sample), "sampled")
print(pd.crosstab(sample["state"], sample["quarter"]).to_string())

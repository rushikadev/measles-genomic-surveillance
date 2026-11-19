"""Pick a balanced sample: D8, 2025+, known state, capped per state per quarter."""
import pandas as pd

CAP = 5
SEED = 42

df = pd.read_csv("data/raw/all_metadata_clean.tsv", sep="\t", parse_dates=["collection_date"])
pool = df[
    (df["genotype_clean"] == "D8")
    & (df["state"] != "Unknown")
    & (df["collection_date"] >= "2025-01-01")
].copy()
pool["quarter"] = pool["collection_date"].dt.to_period("Q").astype(str)

sample = (
    pool.sample(frac=1, random_state=SEED)       # shuffle, reproducibly
        .groupby(["state", "quarter"])
        .head(CAP)
        .sort_values("collection_date")
)
sample.to_csv("data/raw/sample_metadata.tsv", sep="\t", index=False)

print(len(pool), "eligible ->", len(sample), "sampled")
print(pd.crosstab(sample["state"], sample["quarter"]).to_string())

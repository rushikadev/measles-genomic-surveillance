"""Clean state names, genotype and DSId in the full metadata table."""
import pandas as pd
from measles_utils import normalize_state, extract_genotype, extract_dsid

df = pd.read_csv("data/raw/all_metadata.tsv", sep="\t")
df["state"] = normalize_state(df["state"])
df["genotype_clean"] = extract_genotype(df["genotype"])
df["dsid"] = extract_dsid(df["genotype"])
df.to_csv("data/raw/all_metadata_clean.tsv", sep="\t", index=False)

print("States (top 10):")
print(df["state"].value_counts().head(10).to_string())
print("\nYear x genotype:")
print(pd.crosstab(df["year"], df["genotype_clean"].fillna("blank")).to_string())

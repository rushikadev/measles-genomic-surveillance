"""Build a metadata table and filtered FASTA from the downloaded sequences."""
import os
import pandas as pd
from Bio import Entrez, SeqIO

Entrez.email = os.environ["NCBI_EMAIL"]  # set in your shell, not in the repo

IN_FASTA = "data/test/measles_test.fasta"
OUT_META = "data/test/metadata.tsv"
OUT_FASTA = "data/test/measles_test_filtered.fasta"
MIN_LEN = 15700

ids = [r.id for r in SeqIO.parse(IN_FASTA, "fasta")]
handle = Entrez.efetch(db="nucleotide", id=ids, rettype="gb", retmode="text")

rows = []
for r in SeqIO.parse(handle, "genbank"):
    q = r.features[0].qualifiers
    rows.append({
        "accession": r.id,
        "isolate": q.get("isolate", [""])[0],
        "length": len(r.seq),
        "description": r.description,
        "partial": "partial" in r.description.lower(),
        "geo_loc_name": q.get("geo_loc_name", [""])[0],
        "collection_date_raw": q.get("collection_date", [""])[0],
        "genotype": q.get("note", [""])[0].replace("genotype: ", ""),
    })
handle.close()

df = pd.DataFrame(rows)
df["state"] = df["geo_loc_name"].str.replace("USA:", "", regex=False).str.strip()
df["state"] = df["state"].replace({"TX": "Texas", "AZ": "Arizona", "MN": "Minnesota"})
df["collection_date"] = pd.to_datetime(df["collection_date_raw"], format="mixed", errors="coerce")
df["year"] = df["collection_date"].dt.year

keep = (
    (df["length"] >= MIN_LEN)
    & (df["collection_date"] >= "2025-01-01")
    & df["geo_loc_name"].str.startswith("USA")
    & df["collection_date"].notna()
)
print(f"{len(df)} records, {keep.sum()} pass the filter")
print("Dropped:")
print(df.loc[~keep, ["accession", "length", "partial", "collection_date_raw"]].to_string(index=False))

df_keep = df[keep].sort_values("collection_date")
df_keep.to_csv(OUT_META, sep="\t", index=False)

keep_ids = set(df_keep["accession"])
recs = [r for r in SeqIO.parse(IN_FASTA, "fasta") if r.id in keep_ids]
SeqIO.write(recs, OUT_FASTA, "fasta")
print(f"Wrote {len(recs)} sequences to {OUT_FASTA}")
print(df_keep["state"].value_counts().to_string())

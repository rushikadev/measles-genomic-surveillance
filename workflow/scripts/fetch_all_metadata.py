"""Fetch metadata (not sequences) for US measles full-length records, 2020-2026."""
import os, time
import pandas as pd
from Bio import Entrez, SeqIO

Entrez.email = os.environ["NCBI_EMAIL"]
QUERY = ('"Measles morbillivirus"[Organism] AND USA[All Fields] '
         'AND 15700:16000[SLEN] AND 2020/01/01:2026/12/31[PDAT]')

h = Entrez.esearch(db="nucleotide", term=QUERY, retmax=5000)
ids = Entrez.read(h)["IdList"]
print(f"{len(ids)} records to fetch")

rows = []
for i in range(0, len(ids), 100):
    batch = ids[i:i + 100]
    h = Entrez.efetch(db="nucleotide", id=batch, rettype="gb", retmode="text")
    for r in SeqIO.parse(h, "genbank"):
        q = r.features[0].qualifiers
        rows.append({
            "accession": r.id,
            "isolate": q.get("isolate", [""])[0],
            "length": len(r.seq),
            "geo_loc_name": q.get("geo_loc_name", [""])[0],
            "collection_date_raw": q.get("collection_date", [""])[0],
            "genotype": q.get("note", [""])[0].replace("genotype: ", ""),
            "release_date": r.annotations.get("date", ""),
        })
    print(f"  fetched {min(i + 100, len(ids))}/{len(ids)}")
    time.sleep(0.5)

df = pd.DataFrame(rows)
df["state"] = (df["geo_loc_name"].str.replace("USA:", "", regex=False).str.strip()
               .replace({"TX": "Texas", "AZ": "Arizona", "MN": "Minnesota"}))
df["collection_date"] = pd.to_datetime(df["collection_date_raw"], format="mixed", errors="coerce")
df["year"] = df["collection_date"].dt.year
df.to_csv("data/raw/all_metadata.tsv", sep="\t", index=False)

print("\nRecords by collection year:")
print(df["year"].value_counts(dropna=False).sort_index().to_string())
print("\nTop states:")
print(df["state"].value_counts().head(12).to_string())
print("\nGenotypes:")
print(df["genotype"].value_counts().to_string())

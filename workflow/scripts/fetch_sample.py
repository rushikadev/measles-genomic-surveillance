"""Download FASTA for the accessions listed in the sample table."""
import os, time
import pandas as pd
from Bio import Entrez, SeqIO

Entrez.email = os.environ["NCBI_EMAIL"]
acc = pd.read_csv("data/raw/sample_metadata.tsv", sep="\t")["accession"].tolist()

with open("data/raw/sample.fasta", "w") as out:
    for i in range(0, len(acc), 100):
        h = Entrez.efetch(db="nucleotide", id=acc[i:i + 100], rettype="fasta", retmode="text")
        out.write(h.read())
        time.sleep(0.5)

n = sum(1 for _ in SeqIO.parse("data/raw/sample.fasta", "fasta"))
print(f"requested {len(acc)}, wrote {n}")

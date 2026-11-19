"""Fetch a small set of US measles sequences from NCBI nucleotide."""
import sys
from Bio import Entrez, SeqIO

Entrez.email = "rushika.devineni@gmail.com"  # NCBI requires a real email

QUERY = (
    '"Measles morbillivirus"[Organism] AND USA[All Fields] '
    'AND 2025/01/01:2026/12/31[PDAT]'
)
MAX_SEQS = 50
OUT = "data/raw/measles_us_test.fasta"

# 1. How many records match?
handle = Entrez.esearch(db="nucleotide", term=QUERY, retmax=MAX_SEQS)
result = Entrez.read(handle)
handle.close()
print(f"Total matching records: {result['Count']}")
ids = result["IdList"]
if not ids:
    sys.exit("No records found. Try loosening the query.")

# 2. Download them as FASTA
handle = Entrez.efetch(db="nucleotide", id=ids, rettype="fasta", retmode="text")
with open(OUT, "w") as f:
    f.write(handle.read())
handle.close()

# 3. Quick summary so we can see what we got
records = list(SeqIO.parse(OUT, "fasta"))
print(f"Saved {len(records)} sequences to {OUT}")
for r in records[:10]:
    print(f"{len(r.seq):>6} bp  {r.description[:90]}")

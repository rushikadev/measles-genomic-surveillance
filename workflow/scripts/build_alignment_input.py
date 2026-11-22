"""Download outgroup genomes and combine them with the sample FASTA.

The four 2019 California genomes are the outgroup used for rooting. The 2024
Thailand genome is included as an ordinary tip (it nests inside the US sequences).
"""
import os
from Bio import Entrez, SeqIO

Entrez.email = os.environ["NCBI_EMAIL"]
EXTRA = ["MT789821.1", "MT789830.1", "MT789840.1", "MT789849.1", "PP626047.1"]

h = Entrez.efetch(db="nucleotide", id=EXTRA, rettype="fasta", retmode="text")
open("data/raw/outgroups.fasta", "w").write(h.read())

sample = list(SeqIO.parse("data/raw/sample.fasta", "fasta"))
extra = list(SeqIO.parse("data/raw/outgroups.fasta", "fasta"))
SeqIO.write(sample + extra, "data/raw/sample_with_outgroups.fasta", "fasta")
print(f"{len(sample)} sampled + {len(extra)} extra = {len(sample) + len(extra)}")

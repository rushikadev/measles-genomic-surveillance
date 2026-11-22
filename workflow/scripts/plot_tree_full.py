"""Plot the 251-tip ML tree: rooted on 2019 California, tips colored by state."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from Bio import Phylo

CAL = {"MT789821.1", "MT789830.1", "MT789840.1", "MT789849.1"}
THAI = "PP626047.1"
N_COLORED = 7

meta = pd.read_csv("data/raw/sample_metadata.tsv", sep="\t")
state_of = dict(zip(meta["accession"], meta["state"]))
top = meta["state"].value_counts().head(N_COLORED).index.tolist()

def group(name):
    if name in CAL:
        return "2019 California (outgroup)"
    if name == THAI:
        return "Thailand 2024"
    s = state_of.get(name, "Other")
    return s if s in top else "Other states"

tree = Phylo.read("results/measles_full.treefile", "newick")
outs = [t for t in tree.get_terminals() if t.name in CAL]
tree.root_with_outgroup(tree.common_ancestor(outs))
tree.ladderize()

x = tree.depths()
y = {}
for i, t in enumerate(tree.get_terminals()):
    y[t] = i
def fill_y(c):
    if not c.is_terminal():
        y[c] = sum(fill_y(ch) for ch in c.clades) / len(c.clades)
    return y[c]
fill_y(tree.root)

groups = top + ["Other states", "Thailand 2024", "2019 California (outgroup)"]
cmap = plt.get_cmap("tab10")
colors = {g: cmap(i) for i, g in enumerate(top)}
colors.update({"Other states": "#bbbbbb", "Thailand 2024": "black",
               "2019 California (outgroup)": "#17becf"})

fig, ax = plt.subplots(figsize=(9, 12))
for c in tree.get_nonterminals():
    kids = [y[ch] for ch in c.clades]
    ax.plot([x[c], x[c]], [min(kids), max(kids)], color="0.4", lw=0.5)
    for ch in c.clades:
        ax.plot([x[c], x[ch]], [y[ch], y[ch]], color="0.4", lw=0.5)

tips = tree.get_terminals()
for g in groups:
    pts = [t for t in tips if group(t.name) == g]
    ax.scatter([x[t] for t in pts], [y[t] for t in pts], s=14,
               color=colors[g], label=f"{g} (n={len(pts)})", zorder=3)

ax.set_yticks([])
ax.set_xlabel("Substitutions per site")
ax.set_title(f"US measles D8 genomes (n={len(tips)}), ML tree rooted on 2019 California")
for side in ("top", "right", "left"):
    ax.spines[side].set_visible(False)
ax.legend(loc="upper left", fontsize=8, frameon=False)
plt.tight_layout()
plt.savefig("results/tree_full.png", dpi=200)
print("Saved results/tree_full.png")

"""Plot the ML tree with tips colored by US state."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from Bio import Phylo
from matplotlib.patches import Patch

meta = pd.read_csv("data/test/metadata.tsv", sep="\t")
meta["state"] = meta["state"].replace({"USA": "Unknown"})
state_of = dict(zip(meta["accession"], meta["state"]))
date_of = dict(zip(meta["accession"], pd.to_datetime(meta["collection_date"]).dt.strftime("%Y-%m")))

states = sorted(meta["state"].unique())
cmap = plt.get_cmap("tab10")
color_of = {s: cmap(i % 10) for i, s in enumerate(states)}

tree = Phylo.read("results/measles.treefile", "newick")
tree.root_at_midpoint()
tree.ladderize()

label_colors = {t.name: color_of[state_of[t.name]] for t in tree.get_terminals()}

fig, ax = plt.subplots(figsize=(12, 9))
Phylo.draw(
    tree,
    axes=ax,
    do_show=False,
    show_confidence=False,
    label_func=lambda c: f"{c.name} ({state_of[c.name]}, {date_of[c.name]})" if c.is_terminal() else "",
    label_colors=lambda name: label_colors.get(name.split(" ")[0], "black"),
)
ax.set_title("US measles D8 genomes, ML tree (K3Pu+F)")
ax.legend(
    handles=[Patch(color=color_of[s], label=s) for s in states],
    title="State", loc="lower left",
)
xmax = max(tree.depths().values())
ax.set_xlim(-0.0003, xmax * 2.0)   # leave room on the right for tip labels
for side in ("top", "right"):
    ax.spines[side].set_visible(False)
plt.tight_layout()
plt.savefig("results/tree.png", dpi=200)
print("Saved results/tree.png")

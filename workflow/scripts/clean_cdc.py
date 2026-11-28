"""Clean the CDC SchoolVaxView kindergarten export to a state-level MMR table."""
import sys
import pandas as pd
from measles_utils import ABBR, clean_cdc_mmr

SRC = (sys.argv[1] if len(sys.argv) > 1 else
       "data/raw/Vaccination_Coverage_and_Exemptions_among_Kindergartners_20261123.csv")
out = clean_cdc_mmr(pd.read_csv(SRC))
out.to_csv("data/raw/cdc_mmr_state.csv", index=False)

cur = out[out["school_year"] == "2025-26"]
print(len(out), "rows,", out["school_year"].nunique(), "school years")
print("2025-26 geographies not in the 50 states + DC:",
      sorted(set(cur["state"]) - set(ABBR.values())))
print("2025-26 missing coverage:", int(cur["mmr_coverage"].isna().sum()))
print("2025-26 not a full census:", int((~cur["full_census"]).sum()))
print("\nLowest 5 states, 2025-26:")
print(cur.nsmallest(5, "mmr_coverage")[["state", "mmr_coverage", "percent_surveyed"]].to_string(index=False))

"""Pure helper functions for the measles pipeline (importable and testable)."""
import pandas as pd

ABBR = {
 "AL":"Alabama","AK":"Alaska","AZ":"Arizona","AR":"Arkansas","CA":"California",
 "CO":"Colorado","CT":"Connecticut","DE":"Delaware","FL":"Florida","GA":"Georgia",
 "HI":"Hawaii","ID":"Idaho","IL":"Illinois","IN":"Indiana","IA":"Iowa","KS":"Kansas",
 "KY":"Kentucky","LA":"Louisiana","ME":"Maine","MD":"Maryland","MA":"Massachusetts",
 "MI":"Michigan","MN":"Minnesota","MS":"Mississippi","MO":"Missouri","MT":"Montana",
 "NE":"Nebraska","NV":"Nevada","NH":"New Hampshire","NJ":"New Jersey","NM":"New Mexico",
 "NY":"New York","NC":"North Carolina","ND":"North Dakota","OH":"Ohio","OK":"Oklahoma",
 "OR":"Oregon","PA":"Pennsylvania","RI":"Rhode Island","SC":"South Carolina",
 "SD":"South Dakota","TN":"Tennessee","TX":"Texas","UT":"Utah","VT":"Vermont",
 "VA":"Virginia","WA":"Washington","WV":"West Virginia","WI":"Wisconsin","WY":"Wyoming",
 "DC":"District of Columbia",
}


def normalize_state(series):
    """Expand state abbreviations; country-only or missing values become 'Unknown'."""
    s = series.fillna("").str.strip().replace(ABBR)
    return s.replace({"USA": "Unknown", "": "Unknown"})


def extract_genotype(series):
    """Pull the trailing genotype (e.g. D8, B3) out of messy GenBank note text."""
    return series.fillna("").str.extract(r"\b([ABDGH]\d{0,2})\s*$")[0]


def extract_dsid(series):
    """Pull the Distinct Sequence ID number out of the note text."""
    return series.fillna("").str.extract(r"DSId\)\s*(\d+)")[0]


def select_pool(df, genotype="D8", start="2025-01-01"):
    """Records eligible for sampling: right genotype, known state, recent enough."""
    return df[
        (df["genotype_clean"] == genotype)
        & (df["state"] != "Unknown")
        & (df["collection_date"] >= start)
    ].copy()


def balanced_sample(pool, cap=5, seed=42):
    """At most `cap` records per state per quarter, chosen reproducibly."""
    pool = pool.copy()
    pool["quarter"] = pool["collection_date"].dt.to_period("Q").astype(str)
    return (
        pool.sample(frac=1, random_state=seed)
            .groupby(["state", "quarter"])
            .head(cap)
            .sort_values("collection_date")
    )


def clean_cdc_mmr(df):
    """State-level MMR coverage from the CDC SchoolVaxView kindergarten export.

    Keeps the plain 'MMR' series (the headline figure), drops national rows, and
    turns non-numeric codes (NReq, NR, ...) into missing values.
    """
    out = df[(df["Vaccine/Exemption"] == "MMR") & (df["Geography Type"] == "States")].copy()
    out["mmr_coverage"] = pd.to_numeric(out["Estimate (%)"], errors="coerce")
    out["state"] = out["Geography"]
    out["school_year"] = out["School Year"]
    out["percent_surveyed"] = out["Percent Surveyed"]
    out["survey_type"] = out["Survey Type"]
    out["full_census"] = out["Survey Type"].fillna("").str.strip().str.lower() == "census"
    cols = ["state", "school_year", "mmr_coverage", "percent_surveyed",
            "survey_type", "full_census"]
    return out[cols].reset_index(drop=True)

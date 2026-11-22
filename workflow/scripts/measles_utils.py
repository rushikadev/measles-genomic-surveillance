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

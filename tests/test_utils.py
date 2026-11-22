import pandas as pd
from measles_utils import (
    normalize_state, extract_genotype, extract_dsid, select_pool, balanced_sample,
)


def make_df():
    rows = [
        {"accession": f"A{i}", "state": "Texas", "genotype_clean": "D8",
         "collection_date": pd.Timestamp("2025-02-01") + pd.Timedelta(days=i)}
        for i in range(12)
    ]
    rows += [
        {"accession": "old", "state": "Texas", "genotype_clean": "D8",
         "collection_date": pd.Timestamp("2024-12-31")},
        {"accession": "b3", "state": "Texas", "genotype_clean": "B3",
         "collection_date": pd.Timestamp("2025-02-01")},
        {"accession": "unk", "state": "Unknown", "genotype_clean": "D8",
         "collection_date": pd.Timestamp("2025-02-01")},
    ]
    return pd.DataFrame(rows)


def test_state_abbreviations_expand():
    s = pd.Series(["TX", "SC", " Texas ", "New Mexico"])
    assert normalize_state(s).tolist() == ["Texas", "South Carolina", "Texas", "New Mexico"]


def test_missing_or_country_only_state_is_unknown():
    s = pd.Series(["USA", "", None])
    assert normalize_state(s).tolist() == ["Unknown"] * 3


def test_genotype_from_plain_and_dsid_labels():
    s = pd.Series(["D8", "Distinct Sequence ID (DSId) 9171; D8",
                   "Lineage: MVs/GirSomnath.IND/42.16/; D8", "B3", "", None])
    out = extract_genotype(s)
    assert out.tolist()[:4] == ["D8", "D8", "D8", "B3"]
    assert out.iloc[4:].isna().all()


def test_dsid_only_label_has_no_genotype():
    out = extract_genotype(pd.Series(["Distinct Sequence ID (DSId) 9171"]))
    assert pd.isna(out.iloc[0])


def test_dsid_extracted():
    out = extract_dsid(pd.Series(["Distinct Sequence ID (DSId) 9171; D8", "D8"]))
    assert out.iloc[0] == "9171"
    assert pd.isna(out.iloc[1])


def test_pool_excludes_old_non_d8_and_unknown_state():
    pool = select_pool(make_df())
    assert set(pool["accession"]) == {f"A{i}" for i in range(12)}


def test_sample_caps_per_state_per_quarter():
    sample = balanced_sample(select_pool(make_df()), cap=5)
    assert len(sample) == 5


def test_sample_is_reproducible():
    pool = select_pool(make_df())
    a = balanced_sample(pool, cap=5, seed=42)["accession"].tolist()
    b = balanced_sample(pool, cap=5, seed=42)["accession"].tolist()
    assert a == b


def test_committed_sample_respects_cap():
    df = pd.read_csv("data/raw/sample_metadata.tsv", sep="\t")
    assert df.groupby(["state", "quarter"]).size().max() <= 5

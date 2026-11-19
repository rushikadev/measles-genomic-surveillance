"""Clean state names, genotype and DSId in the full metadata table."""
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

df = pd.read_csv("data/raw/all_metadata.tsv", sep="\t")
df["state"] = df["state"].fillna("").str.strip().replace(ABBR)
df["state"] = df["state"].replace({"USA": "Unknown", "": "Unknown"})

df["genotype_clean"] = df["genotype"].fillna("").str.extract(r"\b([ABDGH]\d{0,2})\s*$")[0]
df["dsid"] = df["genotype"].fillna("").str.extract(r"DSId\)\s*(\d+)")[0]

df.to_csv("data/raw/all_metadata_clean.tsv", sep="\t", index=False)

print("States (top 10):")
print(df["state"].value_counts().head(10).to_string())

print("\nYear x genotype:")
print(pd.crosstab(df["year"], df["genotype_clean"].fillna("blank")).to_string())

print("\nTop DSIds:")
print(df["dsid"].value_counts().head(8).to_string())

top = df["state"].value_counts().head(8).index
print("\nTop states x year:")
print(pd.crosstab(df[df["state"].isin(top)]["state"],
                  df[df["state"].isin(top)]["year"]).to_string())

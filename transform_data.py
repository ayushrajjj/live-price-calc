# transform_data.py

import pandas as pd
from core.utils import resolve_company

df = pd.read_csv("raw_data.csv")

df["Company"] = df["share_name"].apply(resolve_company)

df = df.sort_values(
    ["Company", "dealer", "price"],
    ascending=[True, True, True]
).reset_index(drop=True)

df.insert(0, "S.No", range(1, len(df) + 1))

final_df = df[[
    "S.No",
    "Company",
    "dealer",
    "price",
    "date"
]].rename(columns={
    "dealer": "Dealer",
    "price": "Price",
    "date": "Last Updated"
})

final_df.to_csv("final_clean_data.csv", index=False)

print("Clean data generated: final_clean_data.csv")

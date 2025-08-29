import os

import pandas as pd


def deduplicated(
    file_path: str,
    column_names: list[str],
    keep="last",
):
    if os.path.exists(file_path):
        existing_df = pd.read_csv(file_path, encoding="utf-8")
        existing_df.drop_duplicates(subset=column_names, keep=keep, inplace=True)
        existing_df.to_csv(file_path, index=False, encoding="utf-8")

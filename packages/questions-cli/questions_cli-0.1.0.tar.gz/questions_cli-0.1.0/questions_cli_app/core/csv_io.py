import pandas as pd
from typing import Iterator, Dict, Any, Optional, List


REQUIRED_COL = "input"


def read_csv_rows(path: str, delimiter: str = ",", limit: Optional[int] = None) -> Iterator[Dict[str, Any]]:
    df = pd.read_csv(path, delimiter=delimiter)
    if REQUIRED_COL not in df.columns:
        raise ValueError(f"CSV missing required column '{REQUIRED_COL}'")
    if limit is not None:
        df = df.head(limit)
    df = df.fillna("")
    for idx, row in df.iterrows():
        yield {
            "input": str(row.get("input", "")).strip(),
            "row_index": int(idx),
        }


def write_csv_with_column(src_path: str, delimiter: str, output_path: str, column_name: str, values: List[Any]) -> None:
    df = pd.read_csv(src_path, delimiter=delimiter)
    if len(values) < len(df):
        pad = ["error"] * (len(df) - len(values))
        values = list(values) + pad
    if len(values) != len(df):
        raise ValueError("Length of values does not match number of rows in CSV")
    df[column_name] = values
    df.to_csv(output_path, index=False) 
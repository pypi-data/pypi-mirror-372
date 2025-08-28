import pandas as pd
from typing import Iterator, Dict, Any, Optional, List


ACCEPTED_INPUT_COLS = ["input", "query", "Input"]


def read_csv_rows(path: str, delimiter: str = ",", limit: Optional[int] = None) -> Iterator[Dict[str, Any]]:
    df = pd.read_csv(path, delimiter=delimiter)
    # Detect which input column exists
    input_col = next((c for c in ACCEPTED_INPUT_COLS if c in df.columns), None)
    if not input_col:
        raise ValueError(f"CSV missing required column. Provide one of: {', '.join(ACCEPTED_INPUT_COLS)}")
    if limit is not None:
        df = df.head(limit)
    df = df.fillna("")
    for idx, row in df.iterrows():
        yield {
            "input": str(row.get(input_col, "")).strip(),
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
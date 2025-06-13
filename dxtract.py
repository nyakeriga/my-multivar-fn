"""
dxtract.py
==========

• Accepts a list-of-dicts representing the “DXtract” table.
• Validates that **every cell is numeric** – otherwise raises
  ValueError("DXtract must be numeric").
• Multiplies all numeric values by 2 (placeholder logic).
• Preserves the original shape (rows, columns, headers).
• Returns a list-of-dicts so Power Query unpacks directly to a table.
"""

from __future__ import annotations
from typing import Any, Dict, List
import pandas as pd


def transform(dxtract_data: List[Dict[str, Any]], params: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Parameters
    ----------
    dxtract_data : list[dict]
        Table from the named range **DXtract**.
    params : dict
        Single-row dict from the named range **Params** (unused for *2 logic).

    Returns
    -------
    list[dict]
        Transformed DXtract table, identical shape, ready for JSON.

    Raises
    ------
    ValueError
        If any cell in DXtract is not numeric.
    """
    df = pd.DataFrame(dxtract_data)

    # Try coercing all values to numeric – invalid cells become NaN
    df_numeric = df.apply(pd.to_numeric, errors="coerce")

    if df_numeric.isna().any().any():
        raise ValueError("DXtract must be numeric")

    df_out = df_numeric * 2

    return df_out.to_dict(orient="records")



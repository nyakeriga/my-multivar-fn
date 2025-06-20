from typing import Any, Dict, List
import pandas as pd

def transform(dxtract_data: List[Dict[str, Any]], params: Dict[str, Any]) -> List[Dict[str, Any]]:
    # Validate all DXtract values are numeric
    df = pd.DataFrame(dxtract_data)
    df_numeric = df.apply(pd.to_numeric, errors="coerce")

    if df_numeric.isna().any().any():
        raise ValueError("DXtract must be numeric")

    # Use multiplier from Params, or default to 2
    multiplier = params.get("Multiplier", 2)
    try:
        multiplier = float(multiplier)
    except ValueError:
        multiplier = 2

    # Multiply and return
    df_out = df_numeric * multiplier
    df_out.columns = df_out.columns.map(str)
    return df_out.to_dict(orient="records")


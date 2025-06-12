# HttpProcess/__init__.py
import json
import logging
from typing import Any, Dict, List

import azure.functions as func
from ..dxtract import transform   # <- your new logic lives in dxtract.py


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("HttpProcess received a request")

    # ─────────────────────────────────────────────────────────────
    # 1️⃣  Parse and validate the JSON body
    # ─────────────────────────────────────────────────────────────
    try:
        body: Dict[str, Any] = req.get_json()
    except ValueError:
        return func.HttpResponse("Invalid JSON body", status_code=400)

    params  = body.get("Params")      # single-row dict
    dxtract = body.get("DXtract")     # list of row-dicts

    if params is None or dxtract is None:
        return func.HttpResponse(
            "JSON must contain both 'Params' and 'DXtract' keys",
            status_code=400,
        )

    # ─────────────────────────────────────────────────────────────
    # 2️⃣  Transform (delegate to dxtract.py)
    # ─────────────────────────────────────────────────────────────
    try:
        result_table: List[Dict[str, Any]] = transform(dxtract, params)
    except ValueError as ve:  # user/input error (e.g., non-numeric)
        return func.HttpResponse(
            body=json.dumps({"error": str(ve)}),
            status_code=400,
            mimetype="application/json",
        )
    except Exception as exc:  # unexpected server error
        logging.exception("dxtract.transform failed")
        return func.HttpResponse(
            body=json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json",
        )

    # ─────────────────────────────────────────────────────────────
    # 3️⃣  Return JSON table Power Query can load directly
    #     (list-of-dicts preserves columns & rows)
    # ─────────────────────────────────────────────────────────────
    logging.info("Returning transformed table with %d rows", len(result_table))

    return func.HttpResponse(
        body=json.dumps(result_table, default=str),
        status_code=200,
        mimetype="application/json",
    )


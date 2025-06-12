# function_app.py  – Python v2 programming-model entry
import json
import logging
import os
import sys
from typing import Any, Dict, List

import azure.functions as func

# ────────────────────────────────────────────────────────────────
# Ensure the project root (where dxtract.py lives) is on sys.path
# ────────────────────────────────────────────────────────────────
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from dxtract import transform  # ← uses UPDATED dxtract.py

app = func.FunctionApp()

# ────────────────────────────────────────────────────────────────
# POST http://localhost:7071/api/HttpProcess
# ────────────────────────────────────────────────────────────────
@app.route(route="HttpProcess", auth_level=func.AuthLevel.FUNCTION)
def HttpProcess(req: func.HttpRequest) -> func.HttpResponse:
    """
    Accepts either payload style:

      ❶ Top-level keys
        {
          "Params":  { "scale": 2 },
          "DXtract": [ { "var1": 10 }, { "var1": 20 } ]
        }

      ❷ Wrapped in 'data'
        {
          "data": {
            "Params":  { "scale": 2 },
            "DXtract": [ { "var1": 10 }, { "var1": 20 } ]
          }
        }
    """
    logging.info("HttpProcess received request")

    # ─── 1️⃣  Parse JSON safely ───────────────────────────────────────────
    try:
        body: Dict[str, Any] = req.get_json()
    except ValueError:
        return func.HttpResponse("Invalid JSON in request body.", status_code=400)

    # Allow both top-level or wrapped payload
    container = body.get("data", body)

    params  = container.get("Params")
    dxtract = container.get("DXtract")

    if params is None or dxtract is None:
        return func.HttpResponse(
            "JSON must contain both 'Params' and 'DXtract' keys.",
            status_code=400,
        )

    # ─── 2️⃣  Transform via dxtract.py ────────────────────────────────────
    try:
        result_table: List[Dict[str, Any]] = transform(dxtract, params)
    except ValueError as ve:  # validation error (e.g., non-numeric)
        return func.HttpResponse(
            json.dumps({"error": str(ve)}),
            status_code=400,
            mimetype="application/json",
        )
    except Exception:
        logging.exception("dxtract.transform failed")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json",
        )

    # ─── 3️⃣  Return JSON table Power Query can unpack ────────────────────
    return func.HttpResponse(
        json.dumps(result_table, default=str),
        status_code=200,
        mimetype="application/json",
    )


import json
import logging
from typing import Any, Dict, List

import azure.functions as func
from .dxtract import transform  # Corrected import — use relative path

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("HttpProcess received a request")

    # 1️⃣ Parse and validate JSON body
    try:
        body: Dict[str, Any] = req.get_json()
    except ValueError:
        return func.HttpResponse("Invalid JSON body", status_code=400)

    params = body.get("Params")
    dxtract = body.get("DXtract")

    if params is None or dxtract is None:
        return func.HttpResponse(
            "JSON must contain both 'Params' and 'DXtract' keys",
            status_code=400,
        )

    # 2️⃣ Call transformation logic
    try:
        result_table: List[Dict[str, Any]] = transform(dxtract, params)
    except ValueError as ve:
        return func.HttpResponse(
            body=json.dumps({"error": str(ve)}),
            status_code=400,
            mimetype="application/json",
        )
    except Exception as exc:
        logging.exception("dxtract.transform failed")
        return func.HttpResponse(
            body=json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json",
        )

    # 3️⃣ Return table (list of dicts) as JSON
    logging.info("Returning transformed table with %d rows", len(result_table))

    return func.HttpResponse(
        body=json.dumps(result_table, default=str),
        status_code=200,
        mimetype="application/json",
    )


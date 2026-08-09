from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import requests


OPENAPI_URL = "http://localhost:8000/openapi.json"
OUTPUT_DIR = Path(__file__).resolve().parents[1]
CSV_PATH = OUTPUT_DIR / "api_list_snapshot.csv"
XLSX_PATH = OUTPUT_DIR / "api_list_snapshot.xlsx"


def extract_endpoint_rows(spec: dict) -> list[dict]:
    rows = []
    for path, methods in spec.get("paths", {}).items():
        for method_name, method_data in methods.items():
            if method_name.lower() not in {"get", "post", "put", "patch", "delete", "head", "options"}:
                continue

            parameters = []
            for param in method_data.get("parameters", []) or []:
                params = {
                    "name": param.get("name"),
                    "in": param.get("in"),
                    "required": param.get("required", False),
                    "description": param.get("description", ""),
                }
                parameters.append(params)

            rows.append(
                {
                    "path": path,
                    "method": method_name.upper(),
                    "tag": (method_data.get("tags") or [""])[0],
                    "summary": method_data.get("summary", ""),
                    "description": method_data.get("description", ""),
                    "parameters": json.dumps(parameters, ensure_ascii=False),
                }
            )
    return rows


def main() -> None:
    response = requests.get(OPENAPI_URL, timeout=30)
    response.raise_for_status()
    spec = response.json()
    rows = extract_endpoint_rows(spec)

    df = pd.DataFrame(rows)
    df.to_csv(CSV_PATH, index=False, encoding="utf-8-sig")
    df.to_excel(XLSX_PATH, index=False)

    print(f"Exported OpenAPI snapshot to {CSV_PATH} and {XLSX_PATH}")


if __name__ == "__main__":
    main()

import json
import os
import sys
import time
from datetime import datetime

import requests

API_KEY = os.environ["SERPAPI_KEY"]
SCHOLAR_ID = os.environ["GOOGLE_SCHOLAR_ID"]
MAX_TRIES = 3
TIMEOUT = 60


def fetch_author() -> dict:
    last_err = "unknown"
    for attempt in range(1, MAX_TRIES + 1):
        try:
            r = requests.get(
                "https://serpapi.com/search.json",
                params={
                    "engine": "google_scholar_author",
                    "author_id": SCHOLAR_ID,
                    "hl": "en",
                    "api_key": API_KEY,
                },
                timeout=TIMEOUT,
            )
            print(f"HTTP Status: {r.status_code}", flush=True)
            data = r.json()
            if r.status_code == 200 and "cited_by" in data:
                return data
            last_err = data.get("error", f"HTTP {r.status_code}")
        except (requests.RequestException, ValueError) as e:
            last_err = f"{type(e).__name__}: {e}"

        print(f"attempt {attempt}/{MAX_TRIES} failed: {last_err}", flush=True)
        if attempt < MAX_TRIES:
            time.sleep(10 * attempt)

    sys.exit(f"Cannot fetch Google Scholar profile via SerpApi: {last_err}")


def to_int(v) -> int:
    return int(str(v).replace(",", "").strip() or 0)


def split_row(row: dict):
    """Each table row is {"citations": {"all": N, "since_YYYY": M}}."""
    values = next(iter(row.values()))
    all_v = to_int(values.get("all", 0))
    recent = [v for k, v in values.items() if k != "all"]
    return all_v, to_int(recent[0]) if recent else 0


data = fetch_author()
table = data["cited_by"].get("table", [])
if len(table) < 3:
    sys.exit(f"Unexpected SerpApi response: cited_by.table has {len(table)} rows")

(citedby, citedby5y), (hindex, hindex5y), (i10, i10_5y) = (
    split_row(row) for row in table[:3]
)

author: dict = {
    "scholar_id": SCHOLAR_ID,
    "name": data.get("author", {}).get("name", ""),
    "citedby": citedby,
    "citedby5y": citedby5y,
    "hindex": hindex,
    "hindex5y": hindex5y,
    "i10index": i10,
    "i10index5y": i10_5y,
    "cites_per_year": {
        int(g["year"]): to_int(g.get("citations", 0))
        for g in data["cited_by"].get("graph", [])
    },
    "updated": str(datetime.now()),
}
print(f"citations={citedby} h-index={hindex} i10={i10}", flush=True)

os.makedirs("results", exist_ok=True)
with open("results/gs_data.json", "w") as f:
    json.dump(author, f, ensure_ascii=False)

shieldio_data = {
    "schemaVersion": 1,
    "label": "citations",
    "message": f"{author['citedby']}",
}
with open("results/gs_data_shieldsio.json", "w") as f:
    json.dump(shieldio_data, f, ensure_ascii=False)

import json
import os
import sys
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup

API_KEY = os.environ["SCRAPERAPI_KEY"]
SCHOLAR_ID = os.environ["GOOGLE_SCHOLAR_ID"]
PROFILE_URL = f"https://scholar.google.com/citations?user={SCHOLAR_ID}&hl=en"
MAX_TRIES = 4
TIMEOUT = 70  # seconds, ScraperAPI recommends >= 60


def fetch_profile() -> str:
    """Fetch the Scholar profile page through the ScraperAPI HTTP endpoint.

    Fails fast with a clear message instead of retrying for many minutes.
    """
    last_err = "unknown"
    for attempt in range(1, MAX_TRIES + 1):
        try:
            r = requests.get(
                "https://api.scraperapi.com/",
                params={"api_key": API_KEY, "url": PROFILE_URL},
                timeout=TIMEOUT,
            )
            if r.status_code == 200 and "gsc_rsb_st" in r.text:
                return r.text
            last_err = f"HTTP {r.status_code}, profile stats table not found"
        except requests.RequestException as e:
            last_err = type(e).__name__
        print(f"attempt {attempt}/{MAX_TRIES} failed: {last_err}", flush=True)
        time.sleep(5 * attempt)
    sys.exit(f"Cannot fetch Google Scholar profile: {last_err}")


def to_int(text: str) -> int:
    return int(text.replace(",", "").strip() or 0)


html = fetch_profile()
soup = BeautifulSoup(html, "html.parser")

cells = [to_int(td.text) for td in soup.find_all("td", class_="gsc_rsb_std")]
if len(cells) < 6:
    sys.exit(f"Unexpected profile layout: found {len(cells)} index cells")

name_tag = soup.find(id="gsc_prf_in")

author: dict = {
    "scholar_id": SCHOLAR_ID,
    "name": name_tag.text if name_tag else "",
    "citedby": cells[0],
    "citedby5y": cells[1],
    "hindex": cells[2],
    "hindex5y": cells[3],
    "i10index": cells[4],
    "i10index5y": cells[5],
}

try:
    years = [int(y.text) for y in soup.find_all(class_="gsc_g_t")]
    cites = [to_int(c.text) for c in soup.find_all(class_="gsc_g_al")]
    author["cites_per_year"] = dict(zip(years, cites))
except ValueError:
    author["cites_per_year"] = {}

author["updated"] = str(datetime.now())

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

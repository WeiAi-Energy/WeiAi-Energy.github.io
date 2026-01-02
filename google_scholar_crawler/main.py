from scholarly import scholarly, ProxyGenerator
import json
from datetime import datetime
import os

pg = ProxyGenerator()
pg.ScraperAPI(os.environ["SCRAPERAPI_KEY"])

scholarly.use_proxy(pg, pg)

author: dict = scholarly.search_author_id(os.environ["GOOGLE_SCHOLAR_ID"])
scholarly.fill(author, sections=["basics", "indices"])
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

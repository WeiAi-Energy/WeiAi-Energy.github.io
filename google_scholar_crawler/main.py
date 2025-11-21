from scholarly import scholarly
import json
from datetime import datetime
import os

SCHOLAR_ID = "s_dxcLMAAAAJ"

author = scholarly.search_author_id(SCHOLAR_ID)
scholarly.fill(author, sections=["basics", "indices", "counts"])

author["updated"] = datetime.utcnow().isoformat()

os.makedirs("results", exist_ok=True)

with open("results/gs_data.json", "w", encoding="utf-8") as f:
    json.dump(author, f, ensure_ascii=False, indent=2)

shieldio_data = {
    "schemaVersion": 1,
    "label": "citations",
    "message": str(author.get("citedby", 0)),
}

with open("results/gs_data_shieldsio.json", "w", encoding="utf-8") as f:
    json.dump(shieldio_data, f, ensure_ascii=False, indent=2)

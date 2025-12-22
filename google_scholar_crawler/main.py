from scholarly import scholarly, ProxyGenerator
import jsonpickle
import json
from datetime import datetime
import os

pg = ProxyGenerator()
pg.ScraperAPI(os.environ['SCRAPERAPI_KEY'])
scholarly.use_proxy(pg, pg)

author: dict = scholarly.search_author_id(os.environ['GOOGLE_SCHOLAR_ID'])
scholarly.fill(author, sections=['basics', 'indices'])
name = author['name']
author['updated'] = str(datetime.now())
print(json.dumps(author, indent=2))
os.makedirs('results', exist_ok=True)
with open(f'results/gs_data.json', 'w') as outfile:
    json.dump(author, outfile, ensure_ascii=False)

shieldio_data = {
  "schemaVersion": 1,
  "label": "citations",
  "message": f"{author['citedby']}",
}
with open(f'results/gs_data_shieldsio.json', 'w') as outfile:
    json.dump(shieldio_data, outfile, ensure_ascii=False)

import requests
from pathlib import Path
import json

current_directory = Path(__file__).parent.resolve()
json_path = current_directory.parent / 'fetched_data' / 'book_pro.json'


if json_path.exists() and json_path.stat().st_size > 0:
	with open(json_path, "r", encoding="utf-8") as f:
		data_load = json.load(f)
else:
	print("The operation can't be done now.")

count_prev = len(data_load)

for data in data_load:
	authors = data.get("authors", None)
	title = data.get("title")

	if title is None:
		data_load.remove(data)

	if authors is None:
		data_load.remove(data)

with open(json_path, "w") as json_file:
	json.dump(data_load, json_file, indent=4) 



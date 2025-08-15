import requests
from pathlib import Path
import json

current_directory = Path(__file__).parent.resolve()
json_path = current_directory / 'fetched_data' / 'book_sci_fiction.json'

headers = {
    "Authorization": "Bearer jwt_token"
}
response = requests.get("http://127.0.0.1:5000/a/v1/db/add", headers=headers)

if json_path.exists() and json_path.stat().st_size > 0:
	with open(json_path, "r", encoding="utf-8") as f:
		data = json.load(f)
else:
	print("The operation can't be done now.")

for book in data:
	title = data["title"]
	subtitle = data.get("subtitle", None)
	
	authors = data.get("authors", [])
	author1 = authors[0] if len(authors) > 0 else None
	author2 = authors[1] if len(authors) > 1 else None
	author2 = authors[1] if len(authors) > 2 else None
	author2 = authors[1] if len(authors) > 3 else None
	author2 = authors[1] if len(authors) > 4 else None

	description = data["description"]

	imagelink = data.get("imageLinks", {}).get("thumbnail", None)

	publisher = data["publisher"]
	publishedDate = data["publishedDate"]

	
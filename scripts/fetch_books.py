import requests
from pathlib import Path
import json

url = r"https://www.googleapis.com/books/v1/volumes?q=programming&maxResults=40&startIndex=200"
response = requests.get(url)


current_directory = Path(__file__).parent.resolve()

json_path = current_directory / 'json' / 'book_progr.json'

if response.status_code == 200:
	data = response.json()

	books = []

	for item in data.get('items', []):
		book = item.get("volumeInfo", {})
		
		single_book_data = {
		"title" : book.get("title", None),
		"authors" : book.get("authors", None),
		"description" : book.get("description", None),
		"imageLinks" : book.get("imageLinks", None)
		}
		books.append(single_book_data)

	if json_path.exists() and json_path.stat().st_size > 0:
		with open(json_path, "r") as f:
			data_old = json.load(f)

		data_old.extend(books)

		with open(json_path, "w") as json_file:
			json.dump(data_old, json_file, indent=4)

	else:
		with open(json_path, "w") as json_file:
			json.dump(books, json_file, indent=4)

	print(f"Data successfully written to {json_path}")


# to check the length of the extracted data
# if json_path.exists() and json_path.stat().st_size > 0:
# 	with open(json_path, "r") as f:
# 		data_old = json.load(f)
# 	print(len(data_old))
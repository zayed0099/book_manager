import requests
from pathlib import Path
import json

fetch_range = int(input('How many times do you want to iterate over? :'))

def fetch_data(fetch_range):
	index = 0
	current_directory = Path(__file__).parent.resolve()
	json_path = current_directory / 'fetched_data' / 'book_non_fiction.json'
	
	for index in range(1, fetch_range + 1):
		url = f"https://www.googleapis.com/books/v1/volumes?q=non fiction&maxResults=40&startIndex={index}"
		response = requests.get(url)

		if response.status_code == 200:
			data = response.json()

			books = []

			for item in data.get('items', []):
				book = item.get("volumeInfo", {})
				
				single_book_data = {
				"title" : book.get("title", None),
				"subtitle" : book.get("subtitle", None),
				"authors" : book.get("authors", None),
				"description" : book.get("description", None),
				"imageLinks" : book.get("imageLinks", None),
				"publisher" : book.get("publisher", None),
				"publishedDate" : book.get("publishedDate", None),
				"industryIdentifiers" : book.get("industryIdentifiers", None),
				"pageCount" : book.get("pageCount", None),
				"categories" : book.get("categories", None),
				"language" : book.get("language", None),
				}
				books.append(single_book_data)

			if json_path.exists() and json_path.stat().st_size > 0:
				with open(json_path, "r", encoding="utf-8") as f:
					data_old = json.load(f)

				data_old.extend(books)

				with open(json_path, "w", encoding="utf-8") as json_file:
					json.dump(data_old, json_file, ensure_ascii=False, indent=4)

			else:
				with open(json_path, "w", encoding="utf-8") as json_file:
					json.dump(books, json_file, ensure_ascii=False, indent=4)

			index += 40

	print("Data successfully fetched.")

fetch_data(fetch_range)

# to check the length of the extracted data
def check_lenght():
	if json_path.exists() and json_path.stat().st_size > 0:
		json_path = current_directory / 'fetched_data' / 'book_sci_fiction.json'
		with open(json_path, "r") as f:
			data_old = json.load(f)
		print(len(data_old))

# check_lenght()
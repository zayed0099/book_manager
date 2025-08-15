import requests
from pathlib import Path
import json

current_directory = Path(__file__).parent.resolve()
json_path = current_directory / 'fetched_data' / 'book_progr.json'

headers = {
	"Content-Type": "application/json",
	"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc1NTI2ODQ2OSwianRpIjoiZTgyZWM2MWItYjZjMi00MGM5LWFjZmMtOTYxNmRmNWJjNzlmIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6MSwibmJmIjoxNzU1MjY4NDY5LCJjc3JmIjoiMDQ0NzY4YzQtODAzNS00ZWI4LThiZTgtMjRkNDkyNmM1YzQxIiwiZXhwIjoxNzU1MjcyMDY5LCJyb2xlIjoiYWRtaW4ifQ.UNo8c0q0rgSNrEUosJVxBViD6to1cXaf02oPWO6ztK8"
}
url = "http://127.0.0.1:5000/a/v1/db/add"

if json_path.exists() and json_path.stat().st_size > 0:
	with open(json_path, "r", encoding="utf-8") as f:
		data_load = json.load(f)
else:
	print("The operation can't be done now.")

res_count = []
data_count = len(data_load)

for data in data_load:
	title = data.get("title")
	subtitle = data.get("subtitle", None)
	
	authors = data.get("authors", None)
	if authors is not None:
		author1 = authors[0] if len(authors) > 0 else None
		author2 = authors[1] if len(authors) > 1 else None
		author3 = authors[2] if len(authors) > 2 else None
		author4 = authors[3] if len(authors) > 3 else None
		author5 = authors[4] if len(authors) > 4 else None

	description = data.get("description", None)

	imagelink = data.get("imageLinks", {}).get("thumbnail", None)

	publisher = data["publisher"]
	pub_date = data["publishedDate"]

	categories = data.get("categories", None)
	if categories is not None:
		category1 = categories[0] if len(categories) > 0 else None
		category2 = categories[1] if len(categories) > 1 else None

	isbns = data.get("industryIdentifiers", None)
	if isbns is not None:
		isbn1 = isbns[0]["identifier"] if len(isbns) > 0 else None
		isbn2 = isbns[1]["identifier"] if len(isbns) > 1 else None
	
	page_count = data.get("pageCount", None)

	language = data.get("language", None)

	payload = {
		"title" : title,
		"subtitle" : subtitle,
		"author1" : author1,
		"author2" : author2,
		"author3" : author3,
		"author4" : author4,
		"author5" : author5,
		"category1" : category1,
		"category2" : category2,
		"description" : description,
		"isbn1" : isbn1 if isbns is not None else None,
		"isbn2" : isbn2 if isbns is not None else None,
		"imagelink" : imagelink,
		"pub_date" : pub_date,
		"page_count" : page_count,
		"language" : language
	}

	response = requests.post(url, json=payload, headers=headers)
	res_count.append(response.status_code)

succ_req = []
for data in res_count:
	if data in [200, 201]:
		succ_req.append(data)


print(f'''
	Total Book : {data_count}
	Total Request Sent : {len(res_count)}
	Total Successful Request : {len(succ_req)}
	''')
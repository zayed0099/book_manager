import requests
from pathlib import Path
import json

current_directory = Path(__file__).parent.resolve()
json_path = current_directory / 'fetched_data' / 'book_literature.json'

headers = {
	"Content-Type": "application/json",
	"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc1NjQ3NTQ3OSwianRpIjoiYWNiZTk2NDctOTM0Yy00ZjI2LTg3ZjctNmYwOGEyODEzMmI0IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6MSwibmJmIjoxNzU2NDc1NDc5LCJjc3JmIjoiNDU1ZjJlNTgtODA1Yi00ZTU2LTkzNWItZjk3Y2I2ZWEzZmViIiwiZXhwIjoxNzU2NDc5MDc5LCJyb2xlIjoiYWRtaW4ifQ.KEa37ti5lFrOUg7Ml5KbvmwKDisev3lGgYT4Y8VZelc"
}
url = "http://127.0.0.1:5000/univdb/v1/add"

if json_path.exists() and json_path.stat().st_size > 0:
	with open(json_path, "r", encoding="utf-8") as f:
		data_load = json.load(f)
else:
	print("The operation can't be done now.")

res_count = []
res_text = []
data_count = len(data_load)

for data in data_load:
	title = data.get("title", None)
	subtitle = data.get("subtitle", None)
	
	authors = data.get("authors", None)

	description = data.get("description", None)

	imagelink = data.get("imageLinks", {}).get("thumbnail", None)

	publisher = data.get("publisher", 'unknown')
	pub_date = data.get("publishedDate")

	categories_api = data.get("categories", None)
	if isinstance(categories_api, list):
		categories = categories_api
	else:
		categories = None

	isbns = data.get("industryIdentifiers", None)
	if isbns is not None:
		isbn1 = isbns[0]["identifier"] if len(isbns) > 0 else None
		isbn2 = isbns[1]["identifier"] if len(isbns) > 1 else None
	
	page_count = data.get("pageCount", None)

	language = data.get("language", None)

	payload = {
		"title" : title,
		"subtitle" : subtitle,
		"authors" : authors,
		"categories" : categories,
		"description" : description,
		"isbn1" : isbn1 if isbns is not None and len(isbns) > 0 else None,
		"isbn2" : isbn2 if isbns is not None and len(isbns) > 1 else None,
		"imagelink" : imagelink,
		"publisher" : publisher,
		"pub_date" : pub_date,
		"page_count" : page_count,
		"language" : language
	}

	response = requests.post(url, json=payload, headers=headers)
	res_count.append(response.status_code)
	res_text.append(response.text)

succ_req = []
for data in res_count:
	if data in [200, 201]:
		succ_req.append(data)

req_data_path = current_directory / "fetched_data" / "req_info.json"
with open(req_data_path, "w") as json_file:
	json.dump(res_text, json_file, indent=4) 

print(f'''
===================================================================	
	Total Book : {data_count}								      
	Total Request Sent : {len(res_count)}                         
	Total Successful Request : {len(succ_req)}                    
	Total Failed Request : {len(res_count) - len(succ_req)}
	Request response saved in : 
	{req_data_path}   
===================================================================
	''')
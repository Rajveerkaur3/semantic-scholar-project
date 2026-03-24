import requests
import json

url = "https://api.semanticscholar.org/graph/v1/author/search"

params = {
    "query": "Jonathan Boisvert",
    "fields": (
        "authorId,"
        "name,"
        "url,"
        "paperCount,"
        "citationCount,"
        "hIndex,"
        "papers.paperId,"
        "papers.title,"
        "papers.year,"
        "papers.authors",
        "affiliations"
    ),
    "limit": 50
}

response = requests.get(url, params=params)
data = response.json()

with open("Jonathan_Boisvert_authors.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print("Saved Jonathan_Boisvert_authors.json")

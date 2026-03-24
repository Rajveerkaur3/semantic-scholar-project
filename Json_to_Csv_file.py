import json
import csv

# Load JSON
with open("Rajveer_Kaur_authors.json", "r", encoding="utf-8") as f:
    json_data = json.load(f)["data"]

# ---------- authors.csv ----------
with open("authors.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "author_id",
        "name",
        "url",
        "paper_count",
        "citation_count",
        "h_index",
        "affiliations"
    ])

    for author in json_data:
        affiliations = author.get("affiliations", [])
        affiliations_str = "; ".join(affiliations) if affiliations else ""

        writer.writerow([
            author["authorId"],
            author["name"],
            author["url"],
            author["paperCount"],
            author["citationCount"],
            author["hIndex"],
            affiliations_str
        ])

# ---------- papers.csv ----------
with open("papers.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["paper_id", "author_id", "title", "year"])

    for author in json_data:
        for paper in author.get("papers", []):
            writer.writerow([
                paper["paperId"],
                author["authorId"],
                paper["title"],
                paper["year"]
            ])

# ---------- co_authors.csv ----------
unique_rows = set()

for author in json_data:
    main_author_id = author["authorId"]

    for paper in author.get("papers", []):
        paper_id = paper["paperId"]

        for co_author in paper.get("authors", []):
            co_author_id = co_author.get("authorId")

            if co_author_id and co_author_id != main_author_id:
                unique_rows.add((
                    main_author_id,
                    paper_id,
                    co_author_id
                ))

with open("co_authors.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["author_id", "paper_id", "co_author_id"])
    writer.writerows(unique_rows)

print("authors.csv, papers.csv, and co_authors.csv created successfully!")
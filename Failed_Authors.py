import psycopg2
import time
import requests
import json

# ----------- Functions -----------

def querySS(author_id):
    url = "https://api.semanticscholar.org/graph/v1/author/" + str(author_id)
    print("Fetching:", url)
    params = {
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
            "papers.authors,"
            "affiliations"
        ),
        "limit": 50
    }

    response = requests.get(url, params=params)
    data = response.json()

    # Minimal safety check
    if "authorId" not in data:
        print(f"⚠ API limit hit or invalid data for author {author_id} — skipping\n")
        # Keep failed authors for future retry
        with open("failed_authors.txt", "a") as f:
            f.write(str(author_id) + "\n")
        return None

    with open(f"{author_id}_author.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Saved {author_id}_author.json")
    return data

def insert_into_DB(data):
    # Add author
    cursor.execute("""
        INSERT INTO public.authors(
            author_id, name, url, paper_count, citation_count, h_index
        ) VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING;
    """, (
        data["authorId"],
        data["name"],
        data["url"],
        data["paperCount"],
        data["citationCount"],
        data["hIndex"]
    ))

    # Add papers
    for paper in data.get("papers", []):
        cursor.execute("""
            INSERT INTO public.papers(
                paper_id, author_id, title, year
            ) VALUES (%s, %s, %s, %s)
            ON CONFLICT DO NOTHING;
        """, (
            paper["paperId"],
            data["authorId"],
            paper["title"],
            paper["year"] if paper["year"] else 0
        ))

        # Add co-author relations
        for author in paper.get("authors", []):
            cursor.execute("""
                INSERT INTO public.co_author_relations(
                    author_id, paper_id, co_author_id
                ) VALUES (%s, %s, %s)
                ON CONFLICT DO NOTHING;
            """, (
                data["authorId"],
                paper["paperId"],
                author["authorId"] if author["authorId"] else 0
            ))

# Check if author already exists
def author_exists(author_id):
    cursor.execute("SELECT 1 FROM public.authors WHERE author_id = %s;", (author_id,))
    return cursor.fetchone() is not None

# ----------- DB Connection -----------

conn = psycopg2.connect(
    host="localhost",
    database="Jonathan_Semantic_Scholar",
    user="postgres",
    password="rajveer123",
    port="5432"
)
cursor = conn.cursor()

# ----------- Process failed authors -----------

with open("failed_authors.txt") as f:
    failed_ids = f.readlines()

for author_id in failed_ids:
    author_id = author_id.strip()

    # Skip if already in DB
    if author_exists(author_id):
        print("Already in database, skipping:", author_id)
        continue

    data = querySS(author_id)

    if data is None:
        time.sleep(2)
        continue

    insert_into_DB(data)
    conn.commit()
    time.sleep(2)

# ----------- Close DB -----------

cursor.close()
conn.close()
print("Failed authors processed successfully!")
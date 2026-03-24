import psycopg2
import time
import requests
import json

def querySS(author_id):
    url = "https://api.semanticscholar.org/graph/v1/author/" + str(author_id)
    print(url)
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

    # Minimal safety check to avoid KeyError
    if "authorId" not in data:
        print(f"⚠ API limit hit or invalid data for author {author_id} — skipping\n")

        # save failed author id
        with open("failed_authors.txt", "a") as f:
            f.write(str(author_id) + "\n")

        return None

    with open("Jonathan_Boisvert_authors.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print("Saved Jonathan_Boisvert_authors.json")
    return data

def insert_into_DB(data):
    # Adding co-author to Authors table
    query_string = """
    INSERT INTO public.authors(
        author_id, name, url, paper_count, citation_count, h_index
    ) VALUES (%s, %s, %s, %s, %s, %s)
    ON CONFLICT DO NOTHING;
    """
    cursor.execute(query_string, (
        data["authorId"],
        data["name"],
        data["url"],
        data["paperCount"],
        data["citationCount"],
        data["hIndex"]
    ))

    # Papers table
    for paper in data.get("papers", []):
        query_string = """
        INSERT INTO public.papers(
            paper_id, author_id, title, year
        ) VALUES (%s, %s, %s, %s)
        ON CONFLICT DO NOTHING;
        """
        cursor.execute(query_string, (
            paper["paperId"],
            data["authorId"],
            paper["title"],
            paper["year"] if paper["year"] is not None else 0
        ))

        # Co-co-authors table
        for author in paper.get("authors", []):
            query_string = """
            INSERT INTO public.co_author_relations(
                author_id,paper_id, co_author_id 
            ) VALUES (%s, %s, %s)
            ON CONFLICT DO NOTHING;
            """
            cursor.execute(query_string, (
                data["authorId"],
                paper["paperId"],
                author["authorId"] if author["authorId"] is not None else 0,
                
            ))

# ----------- DB Connection -----------

conn = psycopg2.connect(
    host="localhost",
    database="Jonathan_Semantic_Scholar",
    user="postgres",
    password="rajveer123",
    port="5432"
)

cursor = conn.cursor()

# ----------- Function to avoid existing authors -----------

def author_exists(author_id):
    cursor.execute(
        "SELECT 1 FROM public.authors WHERE author_id = %s LIMIT 1;",
        (author_id,)
    )
    return cursor.fetchone() is not None


#Get all the co-authors of a Jon
cursor.execute("""
    SELECT DISTINCT co_author_id
    FROM co_author_relations
             WHERE author_id in ('48426429', '2237141740', '144608597', '146717821', '2326656480', '2274943414', '2279753241', '2351185141');
""")

rows = cursor.fetchall()

for row in rows:
    co_author_id = row[0]

    # Skip authors already in database
    if author_exists(co_author_id):
        print("Already in database, skipping:", co_author_id)
        continue

    #Get data on the co-author of each Jon
    data = querySS(co_author_id)

    if data is None:
        time.sleep(2)
        continue

    insert_into_DB(data)
    conn.commit()
    time.sleep(1.2)

conn.commit()
cursor.close()
conn.close()

print("Co-co-author data inserted successfully!")


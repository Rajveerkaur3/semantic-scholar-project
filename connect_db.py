import psycopg2
import os
import urllib.parse

# connection
conn = psycopg2.connect(
    host="localhost",
    database="Jonathan_Semantic_Scholar",
    user="postgres",
    password="rajveer123",
    port="5432"
)

cursor = conn.cursor()

cursor.execute("SELECT * FROM papers;")

# ----------- HELPER FUNCTIONS -----------

def get_author_name(author_id):
    cursor.execute("""
        SELECT name FROM authors WHERE author_id = %s
    """, (author_id,))
    result = cursor.fetchone()
    return result[0] if result else "Unknown"

def get_common_papers(jon1, jon2, co_author):
    cursor.execute("""
        SELECT DISTINCT p.title
        FROM papers p
        JOIN co_author_relations c1 ON p.paper_id = c1.paper_id
        JOIN co_author_relations c2 ON p.paper_id = c2.paper_id
        JOIN co_author_relations c3 ON p.paper_id = c3.paper_id
        WHERE c1.author_id = %s
        AND c2.author_id = %s
        AND c3.author_id = %s
    """, (jon1, jon2, co_author))
    return cursor.fetchall()

def get_papers(author_id, co_author_id):
    cursor.execute("""
        SELECT DISTINCT p.title
        FROM papers p
        JOIN co_author_relations c1 ON p.paper_id = c1.paper_id
        JOIN co_author_relations c2 ON p.paper_id = c2.paper_id
        WHERE c1.author_id = %s
        AND c2.author_id = %s
    """, (author_id, co_author_id))
    return cursor.fetchall()

# ----------- FILE SETUP -----------

file = open("common_coauthors_output.txt", "w", encoding="utf-8")

if not os.path.exists("results"):
    os.makedirs("results")

jon_list = {"48426429", "2237141740", "144608597", "146717821", "2326656480", '2274943414', '2279753241', '2351185141'}
jon_list_str = '(\'' + "\', \'".join(jon_list) + '\')'

seen = set()
pair_data = {}

# ----------- MAIN LOOP -----------

for jon in jon_list:
    cursor.execute("""
    SELECT DISTINCT co_author_id FROM co_author_relations WHERE author_id = '%s'
    """ % str(jon))
    co_authors = cursor.fetchall()

    for co_author in co_authors:
        cursor.execute("""
        SELECT DISTINCT author_id, co_author_id
        FROM co_author_relations
        WHERE author_id = '%s' AND co_author_id IN %s AND co_author_id <> '%s'
        """ % (co_author[0], jon_list_str, jon))
        rows = cursor.fetchall()

        for row in rows:
            co_author_id = row[0]
            other_jon = row[1]

            pair_key = tuple(sorted([jon, other_jon, co_author_id]))
            if pair_key in seen:
                continue
            seen.add(pair_key)

            jon_name = get_author_name(jon)
            other_jon_name = get_author_name(other_jon)
            co_author_name = get_author_name(co_author_id)

            # -------- TXT FILE --------
            file.write("\n--------------------------------------\n")
            file.write(f"Jonathan 1: {jon_name} ({jon})\n")
            file.write(f"Jonathan 2: {other_jon_name} ({other_jon})\n")
            file.write(f"Common Co-author: {co_author_name} ({co_author_id})\n")

            jon1_papers = get_papers(jon, co_author_id)
            file.write("Jonathan 1 Papers:\n")
            for p in jon1_papers:
                file.write(f" - {p[0]}\n")

            jon2_papers = get_papers(other_jon, co_author_id)
            file.write("\nJonathan 2 Papers:\n")
            for p in jon2_papers:
                file.write(f" - {p[0]}\n")

            shared_papers = get_common_papers(jon, other_jon, co_author_id)
            file.write("\nShared Papers:\n")
            if shared_papers:
                for p in shared_papers:
                    file.write(f" - {p[0]}\n")
            else:
                file.write(" - None\n")

            # -------- STORE CLEAN DATA --------
            pair = tuple(sorted([jon, other_jon]))

            if pair not in pair_data:
                pair_data[pair] = {
                    "jon1": jon,
                    "jon2": other_jon,
                    "jon1_name": jon_name,
                    "jon2_name": other_jon_name,
                    "coauthors": set(),
                    "jon1_papers": set(),
                    "jon2_papers": set(),
                    "shared_papers": set()
                }

            pair_data[pair]["coauthors"].add((co_author_name, co_author_id))

            for p in jon1_papers:
                pair_data[pair]["jon1_papers"].add(p[0])

            for p in jon2_papers:
                pair_data[pair]["jon2_papers"].add(p[0])

            for p in shared_papers:
                pair_data[pair]["shared_papers"].add(p[0])

# ----------- CREATE HTML FILES -----------

for pair, data in pair_data.items():
    jon1 = data["jon1"]
    jon2 = data["jon2"]

    filename = f"results/{jon1}_{jon2}.html"
    html = open(filename, "w", encoding="utf-8")

    html.write("""
    <html>
    <head>
    <title>Author Connection</title>
    <style>
        body { font-family: Arial; margin: 40px; background-color: #f5f5f5; }
        h2 { color: #2c3e50; }
        a { color: blue; font-weight: bold; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
    </head>
    <body>
    """)

    html.write(f"<h2>Link between {data['jon1_name']} ({jon1}) and {data['jon2_name']} ({jon2})</h2>")

    # Author profile links
    html.write(f'<p><a href="https://www.semanticscholar.org/author/{jon1}" target="_blank">View {data["jon1_name"]} Profile</a></p>')
    html.write(f'<p><a href="https://www.semanticscholar.org/author/{jon2}" target="_blank">View {data["jon2_name"]} Profile</a></p>')

    # Jonathan 1 Papers (clickable)
    html.write("<h3>Jonathan 1 Papers:</h3><ul>")
    for p in data["jon1_papers"]:
        link = "https://www.semanticscholar.org/search?q=" + urllib.parse.quote(p)
        html.write(f'<li><a href="{link}" target="_blank">{p}</a></li>')
    html.write("</ul>")

    # Jonathan 2 Papers (clickable)
    html.write("<h3>Jonathan 2 Papers:</h3><ul>")
    for p in data["jon2_papers"]:
        link = "https://www.semanticscholar.org/search?q=" + urllib.parse.quote(p)
        html.write(f'<li><a href="{link}" target="_blank">{p}</a></li>')
    html.write("</ul>")

    # Co-authors (clickable)
    html.write("<h3>Common Co-authors:</h3><ul>")
    for name, cid in data["coauthors"]:
        html.write(f'<li><a href="https://www.semanticscholar.org/author/{cid}" target="_blank">{name} ({cid})</a></li>')
    html.write("</ul>")

    # Shared Papers
    html.write("<h3>Shared Papers:</h3><ul>")
    if data["shared_papers"]:
        for p in data["shared_papers"]:
            link = "https://www.semanticscholar.org/search?q=" + urllib.parse.quote(p)
            html.write(f'<li><a href="{link}" target="_blank">{p}</a></li>')
    else:
        html.write("<li>None</li>")
    html.write("</ul>")

    html.write("</body></html>")
    html.close()

# ----------- CLOSE -----------

file.close()
cursor.close()
conn.close()

print("Database connected successfully!")
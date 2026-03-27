import json

# -------- LOAD JSON --------
with open("Jonathan_Boisvert_authors.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# -------- CREATE HTML --------
html = open("search_results.html", "w", encoding="utf-8")

html.write("""
<html>
<head>
    <title>Author Search</title>
    <style>
        body { font-family: Arial; background-color: #f5f5f5; padding: 30px; }
        h1 { text-align: center; }
        .card {
            background: white;
            padding: 15px;
            margin: 10px;
            border-radius: 10px;
            box-shadow: 0px 2px 8px rgba(0,0,0,0.1);
        }
        a {
            color: blue;
            font-weight: bold;
            text-decoration: none;
        }
    </style>
</head>
<body>

<h1>Jonathan Boisvert Authors</h1>
""")

# -------- LOOP THROUGH JSON --------
for author in data["data"]:
    author_id = author.get("authorId", "N/A")
    name = author.get("name", "N/A")
    papers = author.get("paperCount", 0)
    citations = author.get("citationCount", 0)
    hindex = author.get("hIndex", 0)

    link = f"https://www.semanticscholar.org/author/{author_id}"

    html.write(f"""
    <div class="card">
        <a href="{link}" target="_blank">{name} ({author_id})</a><br>
        Papers: {papers} <br>
        Citations: {citations} <br>
        h-index: {hindex}
    </div>
    """)

html.write("""
</body>
</html>
""")

html.close()

print("HTML created: search_results.html")
import os, glob, hashlib, re, tiktoken, openai, psycopg2, psycopg2.extras as extras
from supabase import create_client
from pgvector.psycopg2 import register_vector

openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL = "text-embedding-3-small"

supabase = create_client(os.environ["SUPA_URL"], os.environ["SUPA_SERVICE_KEY"])
# pg = psycopg2.connect(supabase._supabase_postgrest_client.client.base_url+"?sslmode=require")
pg = psycopg2.connect(
    supabase._supabase_postgrest_client.client.base_url + "?sslmode=require"
)
register_vector(pg); cur = pg.cursor()

tokenizer = tiktoken.get_encoding("cl100k_base")
url_root = "https://docs.ogrealm.xyz/"

def md_to_text(md): return re.sub(r"```.*?```", "", md, flags=re.S)

def chunks(txt, size=400, overlap=50):
    t = tokenizer.encode(txt)
    for i in range(0, len(t), size-overlap):
        yield tokenizer.decode(t[i:i+size]).strip()

def embed(batch): return [d["embedding"] for d in
    openai.Embedding.create(model=MODEL, input=batch)["data"]]

for md_path in glob.glob("**/*.md", recursive=True):
    raw = open(md_path).read()
    sha = hashlib.sha1(raw.encode()).hexdigest()
    cur.execute("select 1 from gitbook_chunks where path=%s and hash=%s limit 1", (md_path, sha))
    if cur.fetchone(): continue

    cks = list(chunks(md_to_text(raw)))
    vecs = embed(cks)

    rows = [(md_path, sha, i, cks[i], psycopg2.Binary(bytes(vecs[i])),
             f"{url_root}{md_path[:-3]}") for i in range(len(cks))]

    extras.execute_values(cur,
        "insert into gitbook_chunks (path,hash,chunk_index,content,embedding,url) values %s on conflict do nothing",
        rows)
    print("↑", md_path, len(cks))

pg.commit(); cur.close(); pg.close()

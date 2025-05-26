#!/usr/bin/env python3
"""
Re-ingest GitBook Markdown → Supabase `gitbook_chunks`
* Embeds with OpenAI (text-embedding-3-small by default)
* Stores deep link in `url` column + metadata JSONB
* Overwrites existing rows so old chunks get their URL filled
"""

import os, glob, hashlib, re, unicodedata, tiktoken
from openai import OpenAI
from supabase import create_client

MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")
client = OpenAI()                       # uses OPENAI_API_KEY from env
supabase = create_client(os.environ["SUPA_URL"], os.environ["SUPA_SERVICE_KEY"])
URL_ROOT = "https://docs.ogrealm.xyz/"

enc = tiktoken.get_encoding("cl100k_base")

# ---------- helpers -----------------------------------------------------
def md_to_text(md: str) -> str:
    return re.sub(r"```.*?```", "", md, flags=re.S)

def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii","ignore").decode()
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[\s-]+", "-", text)

def embed(batch):      # returns list[list[float]]
    data = client.embeddings.create(model=MODEL, input=batch).data
    return [d.embedding for d in sorted(data, key=lambda x: x.index)]

def vec_literal(v):    # pgvector literal '[...]'
    return "[" + ",".join(f"{x:.6f}" for x in v) + "]"

# ---------- ingest loop -------------------------------------------------
for md_path in glob.glob("**/*.md", recursive=True):
    if md_path.lower().endswith(("summary.md", "readme.md")):
        continue                                 # skip scaffolding pages

    raw = open(md_path, encoding="utf-8").read()
    blob_sha = hashlib.sha1(raw.encode()).hexdigest()

    # ----- chunk with heading tracking -----
    buf, chunks, heads = [], [], []
    cur_head = ""
    for line in md_to_text(raw).splitlines():
        if line.startswith("#"):
            cur_head = line.lstrip("#").strip()
        buf.append(line + "\n")
        if len(enc.encode("".join(buf))) >= 400:
            chunks.append("".join(buf).strip())
            heads.append(cur_head)
            buf = buf[-50:]
    if buf:
        chunks.append("".join(buf).strip())
        heads.append(cur_head)

    vecs = embed(chunks)

    rel_path = re.sub(r"^docs/", "", md_path).lower()     # keep .md
    base = URL_ROOT + rel_path[:-3]

    rows = []
    for i, chunk in enumerate(chunks):
        anchor = slugify(heads[i]) if heads[i] else ""
        deep = f"{base}#{anchor}" if anchor else base
        rows.append({
            "path": rel_path,
            "hash": blob_sha,
            "chunk_index": i,
            "content": chunk,
            "embedding": vec_literal(vecs[i]),
            "url": deep,
            "metadata": {
                "url": deep,
                "path": rel_path,
                "heading": heads[i]
            }
        })

    # ✱ overwrite existing rows (no ignore_duplicates) ✱
    supabase.table("gitbook_chunks") \
        .upsert(rows, on_conflict="path,hash,chunk_index") \
        .execute()

    print(f"↑ {md_path}: {len(rows)} chunks upserted")

print("✅ Re-ingest complete")

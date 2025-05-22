#!/usr/bin/env python3
"""
GitBook → Supabase pgvector ingestor (REST only).

Requires repo-level secrets:
  SUPA_URL            e.g. https://xxxx.supabase.co
  SUPA_SERVICE_KEY    service-role key
  OPENAI_API_KEY      embedding model key
(Optionally) EMBED_MODEL  defaults to text-embedding-3-small
"""

import os, glob, hashlib, re
import tiktoken, openai
from supabase import create_client

# ── env ────────────────────────────────────────────────────────────────
openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")

supabase = create_client(os.environ["SUPA_URL"], os.environ["SUPA_SERVICE_KEY"])
url_root = "https://docs.ogrealm.xyz/"

# ── helpers ────────────────────────────────────────────────────────────
tok = tiktoken.get_encoding("cl100k_base")

def md_to_text(md: str) -> str:
    """Strip fenced code blocks; leave headings."""
    return re.sub(r"```.*?```", "", md, flags=re.S)

def chunk(text, size=400, overlap=50):
    ids = tok.encode(text)
    for i in range(0, len(ids), size - overlap):
        yield tok.decode(ids[i : i + size]).strip()

def embed(batch):
    data = openai.Embedding.create(model=MODEL, input=batch)["data"]
    # ensure order by index
    return [d["embedding"] for d in sorted(data, key=lambda x: x["index"])]

def vec_literal(vec):
    # pgvector literal string: [0.123,0.456,…]
    return "[" + ",".join(f"{x:.6f}" for x in vec) + "]"

def sha1(path):
    with open(path, "rb") as f:
        return hashlib.sha1(f.read()).hexdigest()

# ── main ingest loop ───────────────────────────────────────────────────
for md_path in glob.glob("**/*.md", recursive=True):
    raw = open(md_path, encoding="utf-8").read()
    blob_sha = sha1(md_path)

    # skip if this exact file+hash already in DB
    already = supabase.table("gitbook_chunks") \
          .select("id") \
          .eq("path", md_path) \
          .eq("hash", blob_sha) \
          .limit(1) \
          .execute()
    if already.data:
        continue

    chunks = list(chunk(md_to_text(raw)))
    vectors = embed(chunks)

    rows = [
        {
            "path": md_path,
            "hash": blob_sha,
            "chunk_index": i,
            "content": chunks[i],
            "embedding": vec_literal(vectors[i]),
            "url": f"{url_root}{md_path[:-3]}"
        }
        for i in range(len(chunks))
    ]

    supabase.table("gitbook_chunks") \
        .upsert(
            rows,
            on_conflict="path,hash,chunk_index",
            ignore_duplicates=True
        ).execute()

    print(f"↑ {md_path} – {len(rows)} chunks inserted/updated")

print("✅ Ingest complete")

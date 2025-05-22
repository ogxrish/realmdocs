#!/usr/bin/env python3
"""
Sync all Markdown files in this repo to Supabase table `gitbook_chunks`,
embedding each chunk with OpenAI (1.x client).

Secrets required in GitHub Actions:
  SUPA_URL           – e.g. https://xxxx.supabase.co
  SUPA_SERVICE_KEY   – service-role key
  OPENAI_API_KEY     – model key
Optional:
  EMBED_MODEL        – defaults to text-embedding-3-small
"""

import os, glob, hashlib, re
import tiktoken
from openai import OpenAI
from supabase import create_client

# ── env -----------------------------------------------------------------
MODEL   = os.getenv("EMBED_MODEL", "text-embedding-3-small")
client  = OpenAI()                                # picks up OPENAI_API_KEY
supabase = create_client(
    os.environ["SUPA_URL"],
    os.environ["SUPA_SERVICE_KEY"]
)
URL_ROOT = "https://docs.ogrealm.xyz/"

# ── helpers --------------------------------------------------------------
enc = tiktoken.get_encoding("cl100k_base")

def md_to_text(md: str) -> str:
    """Strip fenced code blocks; leave headings."""
    return re.sub(r"```.*?```", "", md, flags=re.S)

def chunk(text, size=400, overlap=50):
    ids = enc.encode(text)
    for i in range(0, len(ids), size - overlap):
        yield enc.decode(ids[i : i + size]).strip()

def embed(batch):
    resp = client.embeddings.create(model=MODEL, input=batch)
    # ensure order is preserved
    return [d.embedding for d in sorted(resp.data, key=lambda x: x.index)]

def vec_literal(vec):
    """Turn [0.1,0.2] into '[0.1,0.2]' for pgvector insertion."""
    return "[" + ",".join(f"{x:.6f}" for x in vec) + "]"

# ── ingest loop ----------------------------------------------------------
for md_path in glob.glob("**/*.md", recursive=True):
    raw = open(md_path, encoding="utf-8").read()
    blob_sha = hashlib.sha1(raw.encode()).hexdigest()

    # skip if this exact version already ingested
    present = supabase.table("gitbook_chunks") \
        .select("id") \
        .eq("path", md_path) \
        .eq("hash", blob_sha) \
        .limit(1) \
        .execute()
    if present.data:
        continue

    chunks  = list(chunk(md_to_text(raw)))
    vectors = embed(chunks)

    rows = [
        {
            "path": md_path,
            "hash": blob_sha,
            "chunk_index": i,
            "content": chunks[i],
            "embedding": vec_literal(vectors[i]),
            "url": f"{URL_ROOT}{md_path[:-3]}"
        }
        for i in range(len(chunks))
    ]

    supabase.table("gitbook_chunks") \
        .upsert(rows,
                on_conflict="path,hash,chunk_index",
                ignore_duplicates=True) \
        .execute()

    print(f"↑ {md_path}: {len(rows)} chunks upserted")

print("✅ Ingest complete")

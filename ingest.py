#!/usr/bin/env python3
"""
Sync every Markdown file to Supabase table `gitbook_chunks`
with pgvector embeddings and deep links.

Secrets (GitHub Action):
  SUPA_URL
  SUPA_SERVICE_KEY    – service-role key
  OPENAI_API_KEY
Optional:
  EMBED_MODEL         – default text-embedding-3-small
"""

import os, glob, hashlib, re, unicodedata
import tiktoken
from openai import OpenAI
from supabase import create_client

# ── env ──────────────────────────────────────────────────────────────
MODEL   = os.getenv("EMBED_MODEL", "text-embedding-3-small")
client  = OpenAI()                                    # gets OPENAI_API_KEY
supabase = create_client(os.environ["SUPA_URL"], os.environ["SUPA_SERVICE_KEY"])
URL_ROOT = "https://docs.ogrealm.xyz/"

enc = tiktoken.get_encoding("cl100k_base")

# ── helpers ──────────────────────────────────────────────────────────
def md_to_text(md: str) -> str:
    """Remove fenced code blocks so embeddings focus on prose."""
    return re.sub(r"```.*?```", "", md, flags=re.S)

def slugify(text: str) -> str:
    """GitBook-style slug from heading text."""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[\s-]+", "-", text)

def chunk_tokens(text, size=400, overlap=50):
    ids = enc.encode(text)
    for i in range(0, len(ids), size - overlap):
        yield enc.decode(ids[i : i + size]).strip()

def embed(batch):
    resp = client.embeddings.create(model=MODEL, input=batch)
    return [d.embedding for d in sorted(resp.data, key=lambda x: x.index)]

def vec_literal(vec):
    return "[" + ",".join(f"{x:.6f}" for x in vec) + "]"

# ── ingest loop ──────────────────────────────────────────────────────
for md_path in glob.glob("**/*.md", recursive=True):
    raw = open(md_path, encoding="utf-8").read()
    blob_sha = hashlib.sha1(raw.encode()).hexdigest()

    # skip identical file+hash
    present = supabase.table("gitbook_chunks") \
        .select("id") \
        .eq("path", md_path) \
        .eq("hash", blob_sha) \
        .limit(1) \
        .execute()
    if present.data:
        continue

    # ----- smarter chunking: track current heading -------------------
    text_lines = md_to_text(raw).splitlines()
    current_heading, buffer = "", []
    chunks, headings = [], []

    for line in text_lines:
        if line.startswith("#"):
            current_heading = line.lstrip("#").strip()
        buffer.append(line + "\n")

        if len(enc.encode("".join(buffer))) >= 400:
            chunks.append("".join(buffer).strip())
            headings.append(current_heading)
            buffer = buffer[-50:]            # overlap

    if buffer:
        chunks.append("".join(buffer).strip())
        headings.append(current_heading)

    vectors = embed(chunks)

    # path without leading docs/ and without .md
    rel_path = re.sub(r"^docs\/", "", md_path)[:-3]    # e.g. power/realm-of-ogs
    base_url = URL_ROOT + rel_path

    rows = []
    for i, chunk in enumerate(chunks):
        anchor   = slugify(headings[i]) if headings[i] else ""
        deep_link = f"{base_url}#{anchor}" if anchor else base_url
        rows.append({
            "path": rel_path + ".md",
            "hash": blob_sha,
            "chunk_index": i,
            "content": chunk,
            "embedding": vec_literal(vectors[i]),
            "url": deep_link,
            "metadata": {
                "path": rel_path + ".md",
                "heading": headings[i],
                "url": deep_link
            }
        })

    supabase.table("gitbook_chunks") \
        .upsert(rows,
                on_conflict="path,hash,chunk_index",
                ignore_duplicates=True) \
        .execute()

    print(f"↑ {md_path}: {len(rows)} chunks upserted")

print("✅ Ingest complete")

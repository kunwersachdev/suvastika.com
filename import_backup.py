#!/usr/bin/env python3
"""One-time importer: downloads the full Supabase backup for suvastika.com.

Reads file lists (list1.txt, list2.txt, list3.txt = blog-images bucket;
list_media_patents.txt = media + patents buckets), downloads every file
from Supabase public storage into storage/, and exports all content
tables from the database REST API into database/.
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request

PROJECT = "nlsmuvtvhnlczqdyfdyo"
ANON_KEY = "sb_publishable_klSh4bLNJ2-ljfvx3kPM4Q_9_CTtYEK"  # publishable client key
STORAGE_BASE = f"https://{PROJECT}.supabase.co/storage/v1/object/public/"
REST_BASE = f"https://{PROJECT}.supabase.co/rest/v1/"

TABLES = [
    "categories", "tags", "products", "posts", "pages", "media",
    "patents", "news", "exhibitions", "downloads", "site_settings",
    "speaking_events",
]


def build_paths():
    paths = []
    for fname in ("list1.txt", "list2.txt", "list3.txt"):
        if not os.path.exists(fname):
            print(f"missing {fname}; nothing to do"); sys.exit(0)
        with open(fname) as fh:
            for line in fh:
                line = line.rstrip("\n")
                if not line:
                    continue
                slug, _, files = line.partition("|")
                if files.strip() == "":
                    paths.append(f"blog-images/{slug}")
                else:
                    for fn in files.split():
                        paths.append(f"blog-images/{slug}/{fn}")
    if os.path.exists("list_media_patents.txt"):
        with open("list_media_patents.txt") as fh:
            for line in fh:
                line = line.rstrip("\n")
                if line:
                    paths.append(line)
    return paths


def download(path):
    out = os.path.join("storage", path)
    if os.path.exists(out) and os.path.getsize(out) > 0:
        return True
    os.makedirs(os.path.dirname(out), exist_ok=True)
    url = STORAGE_BASE + urllib.parse.quote(path)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(url, timeout=60) as r, open(out, "wb") as f:
                f.write(r.read())
            return True
        except Exception as exc:  # noqa: BLE001
            print(f"retry {attempt + 1} for {path}: {exc}")
            time.sleep(2)
    if os.path.exists(out):
        os.remove(out)
    return False


def export_table(table):
    rows, offset = [], 0
    while True:
        url = f"{REST_BASE}{table}?select=*&limit=100&offset={offset}"
        req = urllib.request.Request(url, headers={
            "apikey": ANON_KEY, "Authorization": f"Bearer {ANON_KEY}",
        })
        with urllib.request.urlopen(req, timeout=60) as r:
            batch = json.load(r)
        rows.extend(batch)
        if len(batch) < 100:
            break
        offset += 100
    os.makedirs("database", exist_ok=True)
    with open(f"database/{table}.json", "w") as f:
        json.dump(rows, f, ensure_ascii=False, indent=1)
    print(f"{table}: {len(rows)} rows")


def main():
    paths = build_paths()
    print(f"{len(paths)} storage files to download")
    failed = [p for p in paths if not download(p)]
    print(f"downloaded {len(paths) - len(failed)} ok, {len(failed)} failed")
    for p in failed:
        print("FAILED:", p)
    for t in TABLES:
        try:
            export_table(t)
        except Exception as exc:  # noqa: BLE001
            print(f"table {t} export failed: {exc}")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()

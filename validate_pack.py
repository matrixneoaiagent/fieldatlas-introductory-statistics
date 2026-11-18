#!/usr/bin/env python3
"""Validate the Introductory Statistics 2e Field Atlas pack.

Checks the archive layout, manifest, checksums, SQLite integrity, document and
chunk counts, determinism of a rebuild, and runs the pack's own example
questions through FTS5, printing the top hits.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import zipfile

HERE = Path(__file__).resolve().parent
PACK_DIR = HERE / "pack"
PACK = PACK_DIR / "introductory-statistics-2e-1.0.0.fapack"
REPO = Path("/tmp/opencode/fieldatlas")
STOP = {
    "a", "an", "and", "are", "as", "at", "be", "between", "by", "do", "does",
    "for", "from", "how", "in", "is", "it", "of", "on", "or", "the", "to",
    "what", "when", "where", "which", "who", "why", "you", "your", "with",
    "difference", "calculated", "find", "interpret",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    out = []

    def say(line=""):
        print(line)
        out.append(line)

    say("== archive ==")
    with zipfile.ZipFile(PACK) as archive:
        entries = archive.infolist()
        say(f"entries: {[e.filename for e in entries]}")
        say(f"stored (no compression): {all(e.compress_type == zipfile.ZIP_STORED for e in entries)}")
        say(f"fixed timestamps: {all(e.date_time == (1980, 1, 1, 0, 0, 0) for e in entries)}")
        manifest = json.loads(archive.read("manifest.json"))
        archive.extract("content.sqlite", HERE / "_unpacked")

    say(f"zip test: {zipfile.ZipFile(PACK).testzip() is None}")
    with zipfile.ZipFile(PACK) as archive:
        member = hashlib.sha256(archive.read("content.sqlite")).hexdigest()
    say(f"sqlite inside the zip matches the extracted copy: "
        f"{member == sha256(PACK_DIR / 'content.sqlite')}")
    say(f"pack bytes: {PACK.stat().st_size}")
    say(f"pack sha256: {sha256(PACK)}")

    say()
    say("== manifest ==")
    say(json.dumps(manifest, indent=2, sort_keys=True))
    assert manifest["schemaVersion"] == 1
    assert manifest["type"] == "KNOWLEDGE"
    assert manifest["id"] == "introductory-statistics-2e"
    assert manifest["version"] == "1.0.0"
    assert manifest["license"] == "CC BY-NC-SA 4.0"
    assert manifest["sourceUrls"] == ["https://openstax.org/details/books/introductory-statistics-2e"]
    assert manifest["discovery"]["coverageLevel"] == "broad"
    assert 1 <= len(manifest["discovery"]["exampleQuestions"]) <= 6

    say()
    say("== checksums ==")
    sums = {}
    for line in (PACK_DIR / "SHA256SUMS").read_text(encoding="ascii").splitlines():
        digest, name = line.split("  ", 1)
        sums[name] = digest
    say(f"SHA256SUMS entries: {sorted(sums)}")
    say(f"content.sqlite matches: {sums['content.sqlite'] == sha256(PACK_DIR / 'content.sqlite')}")
    say(f"manifest.json matches:  {sums['manifest.json'] == sha256(PACK_DIR / 'manifest.json')}")
    say(f"pack file matches:      {sums[PACK.name] == sha256(PACK)}")

    say()
    say("== database ==")
    database = sqlite3.connect(HERE / "_unpacked" / "content.sqlite")
    say(f"user_version: {database.execute('PRAGMA user_version').fetchone()[0]}")
    say(f"quick_check: {database.execute('PRAGMA quick_check').fetchone()[0]}")
    say(f"columns: {[r[1] for r in database.execute('PRAGMA table_info(chunks_fts)')]}")
    chunks = database.execute("SELECT count(*) FROM chunks_fts").fetchone()[0]
    docs = database.execute("SELECT count(DISTINCT document_id) FROM chunks_fts").fetchone()[0]
    chars = database.execute("SELECT sum(length(text)) FROM chunks_fts").fetchone()[0]
    empty = database.execute("SELECT count(*) FROM chunks_fts WHERE length(text) = 0").fetchone()[0]
    say(f"chunks: {chunks}")
    say(f"documents: {docs}")
    say(f"chunk chars: {chars}  empty chunks: {empty}")
    say(f"sqlite bytes: {(PACK_DIR / 'content.sqlite').stat().st_size}")
    say(f"chunks per document (min/avg/max): "
        f"{database.execute('SELECT min(c), round(avg(c),2), max(c) FROM (SELECT count(*) c FROM chunks_fts GROUP BY document_id)').fetchone()}")

    say()
    say("== FTS5 example questions ==")
    # (question, text query, expected document, title lookup or None)
    probes = [
        ("What is the difference between a parameter and a statistic?",
         '"parameter" AND "statistic"', "is2e-1-1", '"definitions of statistics"'),
        ("How do you find the median of an even number of observations?",
         'median', "is2e-2-5", '"measures of the center"'),
        ("What is the empirical rule?",
         '"empirical rule"', "is2e-2-7", '"measures of the spread"'),
        ("How is a z-score calculated?",
         '"z-score"', "is2e-6-1", '"standard normal"'),
        ("What is a binomial distribution?",
         '"binomial distribution"', "is2e-4-3", '"binomial distribution"'),
        ("How do you interpret a confidence interval?",
         '"confidence interval"', "is2e-8-1", None),
    ]
    passes = 0
    for question, query, want, title_query in probes:
        rows = database.execute(
            "SELECT document_id, title, bm25(chunks_fts) AS score, substr(text,1,80) "
            "FROM chunks_fts WHERE chunks_fts MATCH ? ORDER BY score LIMIT 5",
            (query,),
        ).fetchall()
        rank = next((i + 1 for i, r in enumerate(rows) if r[0] == want), None)
        ok = rank is not None and rank <= 3
        passes += ok
        say(f"Q: {question}")
        say(f"   text query {query}  ->  {want} at rank {rank}  {'PASS (top 3)' if ok else 'MISS (not top 3)'}")
        for doc_id, title, score, snippet in rows[:3]:
            say(f"     {score:8.3f}  {doc_id:22s} {title[:55]:55s} {' '.join(snippet.split())[:60]}")
        if title_query:
            trows = database.execute(
                "SELECT document_id, title, bm25(chunks_fts) AS score FROM chunks_fts "
                "WHERE chunks_fts MATCH ? ORDER BY score LIMIT 3",
                (f"title:{title_query}",),
            ).fetchall()
            say(f"   title lookup title:{title_query} -> "
                + ", ".join(f"{r[0]} ({r[2]:.3f})" for r in trows))
    say(f"example-question text queries: expected section in top 3 for {passes}/6")
    database.close()

    say()
    say("== rebuild determinism ==")
    hashes = []
    for name in ("rebuild-a", "rebuild-b"):
        target = Path(tempfile.mkdtemp(prefix=f"is2e-{name}-"))
        shutil.rmtree(target)
        subprocess.run(
            [sys.executable, "-m", "packtool.build_pack",
             "--input", str(HERE / "docs.jsonl"), "--output", str(target),
             "--id", manifest["id"], "--version", manifest["version"],
             "--title", manifest["title"], "--license", manifest["license"],
             *sum([["--source-url", u] for u in manifest["sourceUrls"]], []),
             "--coverage-summary", manifest["discovery"]["coverageSummary"],
             *sum([["--example-question", q] for q in manifest["discovery"]["exampleQuestions"]], []),
             "--coverage-level", manifest["discovery"]["coverageLevel"]],
            cwd=REPO, check=True, capture_output=True,
        )
        rebuilt = target / PACK.name
        hashes.append(sha256(rebuilt))
        shutil.rmtree(target)
    say(f"rebuild sha256: {hashes[0]}")
    say(f"byte-identical to shipped pack: {hashes[0] == sha256(PACK) and hashes[1] == hashes[0]}")
    shutil.rmtree(HERE / "_unpacked", ignore_errors=True)

    log = "\n".join(out) + "\n"
    (HERE / "validation.log").write_text(log, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

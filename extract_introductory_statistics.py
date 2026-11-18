#!/usr/bin/env python3
"""Build the Field Atlas corpus for OpenStax *Introductory Statistics 2e*.

Input:  a checkout of openstax/osbooks-introductory-statistics-bundle
        (the official CNXML source of the book) plus the book's table of
        contents from the OpenStax archive JSON, which supplies the exact
        page URLs.
Output: JSONL, one object per Field Atlas knowledge document.

Documents:
  * one per numbered section (e.g. is2e-1-1),
  * one per chapter introduction (is2e-1-introduction),
  * one per chapter composite page that the book publishes separately:
    Key Terms, Chapter Review, Formula Review, Practice,
    Bringing It Together: Practice, Homework,
    Bringing It Together: Homework, References,
  * one per appendix (A-H, including the tables in Appendix H),
  * the Preface.

Conversion rules: nothing is rewritten or summarised. CNXML blocks become
lines; headings, worked examples, exercises, notes, figures (alt text +
caption) and tables (one line per row, cells joined with " | ") are kept in
book order. MathML becomes LaTeX ($...$ inline, $$...$$ display) using the
same converter as tools/packs/extract_openstax_prealgebra.py, which is
imported rather than copied.

Composite pages: the web book publishes, for example, "2-key-terms" as one
page, while the CNXML bundle keeps the glossary of every section in that
section's module. Those blocks are concatenated in book order. Each block is
preceded by the book's own section title so the reader knows which section a
term or exercise came from; no other text is added.

Usage:
  python3 extract_introductory_statistics.py \
      --osbooks /path/to/osbooks-introductory-statistics-bundle-main \
      --toc book.json --out docs.jsonl
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

REPO = Path("/tmp/opencode/fieldatlas")
sys.path.insert(0, str(REPO))
from tools.packs.extract_openstax_prealgebra import (  # noqa: E402
    CNXML, COLLXML, MDML, _flat, _local, module_to_text,
)

BOOK_URL = "https://openstax.org/books/introductory-statistics-2e/pages"
LICENSE_ID = "CC BY-NC-SA 4.0"

# CNXML section class -> composite page slug suffix it feeds.
BUCKETS = {
    "summary": "chapter-review",
    "formula-review": "formula-review",
    "practice": "practice",
    "bring-together-exercises": "bringing-it-together-practice",
    "free-response": "homework",
    "bring-together-homework": "bringing-it-together-homework",
    "references": "references",
}


def strip_title(section, root):
    """Serialise a section without its own <title> (the page title covers it)."""
    clone = ET.Element(section.tag, section.attrib)
    clone.text = section.text
    for child in section:
        if _local(child) == "title":
            continue
        clone.append(child)
    return module_to_text(clone, resolve_link=resolver_for(root))


def module_root(osbooks: Path, mid: str):
    return ET.parse(osbooks / "modules" / mid / "index.cnxml").getroot()


LABELS = {"figure": "Figure", "table": "Table", "example": "Example", "exercise": "Exercise"}


def resolver_for(root):
    """Cross-references: the CNXML <link> carries no text; the renderer fills in the
    target's number, which the source does not have. Use the target's section title,
    or the target's kind, exactly as tools/packs/extract_openstax_prealgebra.py does."""
    by_id = {el.get("id"): el for el in root.iter() if el.get("id")}

    def resolve(link_el):
        target = by_id.get(link_el.get("target-id") or "")
        if target is None:
            return ""
        tag = _local(target)
        if tag == "section":
            title = target.find(f"{{{CNXML}}}title")
            return _flat(title) if title is not None else ""
        return LABELS.get(tag, "")

    return resolve


def chapter_modules(osbooks: Path):
    """[(chapter_title, [module_id, ...]), ...] in book order."""
    root = ET.parse(osbooks / "collections" / "introductory-statistics-2e.collection.xml").getroot()
    chapters = []
    content = root.find(f"{{{COLLXML}}}content")

    def collect(node, acc):
        for child in node:
            if _local(child) == "module":
                acc.append(child.get("document"))
            elif _local(child) == "subcollection":
                inner = child.find(f"{{{COLLXML}}}content")
                if inner is not None:
                    collect(inner, acc)

    for node in content:
        if _local(node) == "subcollection":
            title_el = node.find(f"{{{MDML}}}title")
            mods = []
            inner = node.find(f"{{{COLLXML}}}content")
            if inner is not None:
                collect(inner, mods)
            chapters.append((_flat(title_el), mods))
    # Everything outside the 13 chapter subcollections (Preface, appendices).
    flat = []
    for node in content:
        if _local(node) == "module":
            flat.append(node.get("document"))
    return chapters, flat


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--osbooks", type=Path, required=True)
    ap.add_argument("--toc", type=Path, required=True, help="archive book.json")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    toc = json.loads(args.toc.read_text(encoding="utf-8"))["tree"]
    chapters, flat = chapter_modules(args.osbooks)

    def toc_text(s):
        return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s)).strip()

    toc_chapters = [c for c in toc["contents"] if c.get("toc_type") == "chapter"]
    toc_flat = [c for c in toc["contents"] if c.get("toc_target_type") in ("appendix", "preface")]
    assert len(toc_chapters) == len(chapters), (len(toc_chapters), len(chapters))

    docs = []
    report = []

    # --- Preface -----------------------------------------------------------
    preface_module = flat[0]
    root = module_root(args.osbooks, preface_module)
    content = root.find(f"{{{CNXML}}}content")
    docs.append({
        "document_id": "is2e-preface",
        "title": "Preface",
        "source": f"{BOOK_URL}/preface",
        "license": LICENSE_ID,
        "text": module_to_text(content, resolve_link=resolver_for(root)),
    })
    report.append(("preface", preface_module, len(docs[-1]["text"])))

    appendix_modules = flat[1:]
    appendix_pages = [c for c in toc_flat if c.get("toc_target_type") == "appendix"]
    assert len(appendix_modules) == len(appendix_pages), (appendix_modules, appendix_pages)

    for page, mid in zip(appendix_pages, appendix_modules):
        root = module_root(args.osbooks, mid)
        content = root.find(f"{{{CNXML}}}content")
        title = toc_text(page["title"])
        slug = page["slug"].split("-")[0]  # a, b, ... h
        docs.append({
            "document_id": f"is2e-appendix-{slug}",
            "title": title,
            "source": f"{BOOK_URL}/{page['slug']}",
            "license": LICENSE_ID,
            "text": module_to_text(content, resolve_link=resolver_for(root)),
        })
        report.append((f"appendix {slug}", mid, len(docs[-1]["text"])))

    # --- Chapters ----------------------------------------------------------
    for ch_no, ((ch_title, mods), toc_ch) in enumerate(zip(chapters, toc_chapters), start=1):
        pages = {p["toc_target_type"]: [] for p in toc_ch.get("contents", [])}
        for p in toc_ch.get("contents", []):
            pages.setdefault(p["toc_target_type"], []).append(p)
        toc_sections = pages["numbered-section"]
        intro_page = pages["intro"][0]

        roots = [(mid, module_root(args.osbooks, mid)) for mid in mods]
        section_mods = [(mid, r) for mid, r in roots if (r.get("class") or "") != "introduction"]
        intro_mods = [(mid, r) for mid, r in roots if (r.get("class") or "") == "introduction"]
        assert len(section_mods) == len(toc_sections), (
            ch_no, [r.find(f"{{{CNXML}}}title") for _, r in section_mods], toc_sections)

        # Chapter introduction page.
        assert len(intro_mods) == 1, (ch_no, intro_mods)
        intro_root = intro_mods[0][1]
        docs.append({
            "document_id": f"is2e-{ch_no}-introduction",
            "title": f"{ch_no} {ch_title} \u2014 Introduction",
            "source": f"{BOOK_URL}/{intro_page['slug']}",
            "license": LICENSE_ID,
            "text": module_to_text(intro_root.find(f"{{{CNXML}}}content"), resolve_link=resolver_for(intro_root)),
        })
        report.append((f"ch{ch_no} introduction", intro_mods[0][0], len(docs[-1]["text"])))

        # Numbered sections.
        for sec_no, ((mid, r), page) in enumerate(zip(section_mods, toc_sections), start=1):
            content = r.find(f"{{{CNXML}}}content")
            # Body = everything except the chapter-apparatus section blocks.
            body = ET.Element(content.tag, content.attrib)
            body.text = content.text
            for child in content:
                if _local(child) == "section" and (child.get("class") or "") in BUCKETS:
                    continue
                body.append(child)
            docs.append({
                "document_id": f"is2e-{ch_no}-{sec_no}",
                "title": toc_text(page["title"]),
                "source": f"{BOOK_URL}/{page['slug']}",
                "license": LICENSE_ID,
                "text": module_to_text(body, resolve_link=resolver_for(r)),
            })
            report.append((f"ch{ch_no} sec{sec_no}", mid, len(docs[-1]["text"])))

        # Composite chapter pages.
        section_titles = [toc_text(p["title"]) for p in toc_sections]
        composite = {p["slug"].split("-", 1)[1]: p for p in toc_ch.get("contents", [])
                     if p["toc_target_type"] == "composite-page"}
        # Every apparatus block in the CNXML must have a page that carries it.
        present = {child.get("class") for (_, r) in section_mods
                   for child in r.find(f"{{{CNXML}}}content")
                   if _local(child) == "section"}
        for cls, name in BUCKETS.items():
            if cls in present and name not in composite:
                raise SystemExit(f"chapter {ch_no}: class {cls} has no {name} page")
        for page in toc_ch.get("contents", []):
            target = page["toc_target_type"]
            if target in ("intro", "numbered-section", "index"):
                continue
            suffix = page["slug"].split("-", 1)[1]
            if target == "composite-page":
                if suffix == "solutions":
                    continue  # answers are commented out in the CNXML bundle
                if suffix == "key-terms":
                    parts = []
                    for (mid, r), sec_title in zip(section_mods, section_titles):
                        gl = r.find(f"{{{CNXML}}}glossary")
                        if gl is None:
                            continue
                        text = module_to_text(gl, resolve_link=resolver_for(r))
                        if text:
                            parts.append(f"{sec_title}\n\n{text}")
                    text = "\n\n".join(parts)
                else:
                    wanted = [cls for cls, name in BUCKETS.items() if name == suffix]
                    parts = []
                    for (mid, r), sec_title in zip(section_mods, section_titles):
                        content = r.find(f"{{{CNXML}}}content")
                        for child in content:
                            if _local(child) != "section":
                                continue
                            if (child.get("class") or "") not in wanted:
                                continue
                            block = strip_title(child, r)
                            if block:
                                parts.append(f"{sec_title}\n\n{block}")
                    text = "\n\n".join(parts)
                if not text:
                    continue
                docs.append({
                    "document_id": f"is2e-{ch_no}-{suffix}",
                    "title": toc_text(page["title"]),
                    "source": f"{BOOK_URL}/{page['slug']}",
                    "license": LICENSE_ID,
                    "text": text,
                })
                report.append((f"ch{ch_no} {suffix}", "-", len(text)))

    # --- Write -------------------------------------------------------------
    docs.sort(key=lambda d: d["document_id"])
    ids = [d["document_id"] for d in docs]
    assert len(ids) == len(set(ids)), "duplicate document ids"
    payload = "".join(json.dumps(d, ensure_ascii=False) + "\n" for d in docs)
    args.out.write_text(payload, encoding="utf-8")

    words = sum(len(re.findall(r"\S+", d["text"])) for d in docs)
    print(f"documents: {len(docs)}")
    print(f"words: {words}")
    print(f"chars: {sum(len(d['text']) for d in docs)}")
    print(f"bytes: {len(payload.encode('utf-8'))}")
    print(f"sha256: {hashlib.sha256(payload.encode('utf-8')).hexdigest()}")
    print(f"min/max doc chars: {min(len(d['text']) for d in docs)}/{max(len(d['text']) for d in docs)}")
    for name, mid, n in report:
        print(f"  {name:28s} {mid:8s} {n:7d} chars")


if __name__ == "__main__":
    main()

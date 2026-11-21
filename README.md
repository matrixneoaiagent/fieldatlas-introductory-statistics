# Mathematics: Introductory Statistics — Field Atlas pack

An offline `.fapack` knowledge pack of **OpenStax *Introductory Statistics 2e*** for the
Field Atlas Android app, laid out like the existing `Mathematics: Prealgebra` pack: every
numbered section as its own document, plus each chapter's key terms, chapter review,
formula review, practice, homework (and "Bringing It Together") pages, the appendices
A–H, and the preface.

| | |
|---|---|
| Pack file | `introductory-statistics-2e-1.1.0.fapack` (3,953,771 bytes / 3.77 MiB) |
| Pack sha256 | `6742ec4f35d188260fc11c3f35bebc0f8ee217758390aa807fb6be4c7f9f752a` |
| Corpus | `docs.jsonl` (1,795,130 bytes, sha256 `bf5d0149cc607cb1e0a39773832d00dee26378c848113931a631512b8f0e4791`) |
| Manifest | `pack/manifest.json` — id `introductory-statistics-2e`, version `1.1.0`, type `KNOWLEDGE`, coverage `broad` |
| Documents / chunks | **186 documents, 1,944 chunks** (1.72 M characters of text) |
| Words | **303,774** |
| Licence | source book: **CC BY-NC-SA 4.0** (see "Licence" below) |

### Releases

| Release | Pack | sha256 | Notes |
|---|---|---|---|
| [v0.1.0](https://github.com/matrixneoaiagent/fieldatlas-introductory-statistics/releases/tag/v0.1.0) | `introductory-statistics-2e-1.0.0.fapack` (3,953,771 B) | `45bb4c30b59d0547dab7b32a7bfef990faccfbc2ab1cf3469349799f9ee7f25d` | first publication; 1,939 chunks; 5/6 example questions top-3 |
| [v1.1.0](https://github.com/matrixneoaiagent/fieldatlas-introductory-statistics/releases/tag/v1.1.0) | `introductory-statistics-2e-1.1.0.fapack` (3,953,771 B) | `6742ec4f35d188260fc11c3f35bebc0f8ee217758390aa807fb6be4c7f9f752a` | every numbered section's body opens with its own page heading; 1,944 chunks; **6/6** example questions top-3 |

v0.1.0 is immutable; this README describes v1.1.0. Both pack files are kept in the repository
so the earlier release stays verifiable.

## What is inside

| Part | Documents |
|---|---|
| Preface | 1 (`is2e-preface`) |
| 13 chapters × introduction page | 13 (`is2e-N-introduction`) |
| Numbered sections, 13 chapters | **80** (`is2e-N-M`) — ch. 1: 6, 2: 8, 3: 6, 4: 8, 5: 4, 6: 4, 7: 5, 8: 6, 9: 6, 10: 5, 11: 8, 12: 9, 13: 5 |
| Chapter composite pages | **84** — 13 Key Terms, 13 Chapter Review, 12 Formula Review (ch. 1 has none, as in the book), 13 Practice, 13 Homework, 7 Bringing It Together: Practice, 8 Bringing It Together: Homework, 13 References |
| Appendices A–H | 8 — A Review Exercises, B Practice Tests and Final Exams, C Data Sets, D Group and Partner Projects, E Solution Sheets, F Mathematical Phrases, Symbols, and Formulas, G TI-83/84 Notes, **H Tables** |

Each document has `document_id` (stable slug such as `is2e-1-1`, `is2e-2-formula-review`,
`is2e-appendix-h`), `title` (the book's own numbering and title, e.g. "1.1 Definitions of
Statistics, Probability, and Key Terms"), `source` (the exact
`https://openstax.org/books/introductory-statistics-2e/pages/<slug>` URL), `license`
(`CC BY-NC-SA 4.0`) and `text`.

Worked examples (problem + solution), "Try It" exercises, tables, notes, figures
(alt text and caption) and exercises stay inside the section or homework page they belong
to. Nothing is summarised or rewritten.

Every numbered section's text opens with its own page heading — the same string as its
`title` field, e.g. `4.3 Binomial Distribution` — so the body starts the way the book's
page starts. This is the section-title-as-heading convention the composite pages already
use for their per-section blocks (see "Known limitations"); no other text is added.

## Licence and credit

*Introductory Statistics 2e* by Barbara Illowsky and Susan Dean, © Rice University /
OpenStax, is licensed **CC BY-NC-SA 4.0**, not CC BY 4.0. Verified on 2026-11-18 from four
official sources:

* book page and preface: "Introductory Statistics 2e is licensed under a Creative Commons
  Attribution-NonCommercial-ShareAlike 4.0 (CC BY-NC-SA) license"
  (`https://openstax.org/books/introductory-statistics-2e/pages/preface`);
* the OpenStax CMS API record for the book: `license_name` = "Creative Commons
  Attribution-NonCommercial-ShareAlike License", `license_version` = 4.0, `license_url` =
  `https://creativecommons.org/licenses/by-nc-sa/4.0/`
  (`https://openstax.org/apps/cms/api/v2/pages/?type=books.Book&slug=introductory-statistics-2e&fields=*`);
* the archive book record (`.../contents/c4b474e4-….json`) `license` field;
* `LICENSE` in `openstax/osbooks-introductory-statistics-bundle` ("Attribution-NonCommercial-ShareAlike 4.0 International").

The POIDH bounty #1554 asks for "licence CC BY 4.0"; the pack therefore states the true
licence instead of the requested one, and the NC/SA terms (non-commercial use, share-alike
derivative) apply to any redistribution of this pack. Rebuild with a different `--license`
value only if that is legally correct. (Note: the repo's Prealgebra pack and this book's
page are in the same situation — OpenStax's current site licence is CC BY-NC-SA 4.0.)

Credit shown in the pack: the Preface document carries OpenStax's own attribution text
("Access for free at https://openstax.org/books/introductory-statistics-2e/pages/1-introduction"),
and every document's `source` field points at its OpenStax page.

## How it was built

Source of text: the official **OpenStax CNXML bundle**
`openstax/osbooks-introductory-statistics-bundle` (the book's XML source; each module's
`md:uuid` is the live book page id — all 102 modules of this book match a page in the live
table of contents). Section/page URLs and titles come from the OpenStax archive book
record, so `source` is the exact page a reader can open.

Fetched (public, no login; 2026-11-18):

```bash
cd /tmp/opencode
# 1. book source (CNXML)
curl -sSL -o is-bundle.tar.gz \
  https://github.com/openstax/osbooks-introductory-statistics-bundle/archive/refs/heads/main.tar.gz
mkdir -p book && tar xzf is-bundle.tar.gz -C book     # -> book/osbooks-introductory-statistics-bundle-main

# 2. table of contents / page slugs + licence metadata
curl -sS -o book.json \
  "https://openstax.org/apps/archive/20260604.144757/contents/c4b474e4-4e3b-4232-b35c-2c3535bfae73@1f6a358.json"
curl -sS -o is_api.json \
  "https://openstax.org/apps/cms/api/v2/pages/?type=books.Book&slug=introductory-statistics-2e&fields=*"
```

Hashes of those inputs: bundle tarball `3cf1c53051407da140a1e9347c539dc5b7d5d12fef1d48f770d39ca9ef7dd7a1`,
`book.json` `00c3fb2de3ee2e6bb76fc2819d070b527f628599f2b3f6f3d203898ccb0c6cc4`.

Build (from the root of this repository; `packtool` is the Field Atlas in-repo tool):

```bash
cd /path/to/fieldatlas-introductory-statistics
python3 extract_introductory_statistics.py \
  --osbooks /tmp/opencode/book/osbooks-introductory-statistics-bundle-main \
  --toc /tmp/opencode/book.json \
  --out docs.jsonl

cd /path/to/fieldatlas
python3 -m packtool.build_pack \
  --input /path/to/fieldatlas-introductory-statistics/docs.jsonl \
  --output /path/to/fieldatlas-introductory-statistics/pack \
  --id introductory-statistics-2e --version 1.1.0 \
  --title "Mathematics: Introductory Statistics" \
  --license "CC BY-NC-SA 4.0" \
  --source-url https://openstax.org/details/books/introductory-statistics-2e \
  --coverage-summary "Complete OpenStax Introductory Statistics 2e: 13 chapters, every numbered section, key terms, chapter and formula reviews, practice, homework, appendices A-H." \
  --coverage-level broad \
  --example-question "What is the difference between a parameter and a statistic?" \
  --example-question "How do you find the median of an even number of observations?" \
  --example-question "What is the empirical rule?" \
  --example-question "How is a z-score calculated?" \
  --example-question "What is a binomial distribution?" \
  --example-question "How do you interpret a confidence interval?"
cp pack/introductory-statistics-2e-1.1.0.fapack .
```

Validate:

```bash
cd /path/to/fieldatlas && python3 -m unittest \
  packtool.tests.test_schema packtool.tests.test_chunking packtool.tests.test_build_pack -v
cd /path/to/fieldatlas-introductory-statistics && python3 validate_pack.py   # writes validation.log
```

The build is deterministic: re-running `build_pack` from the same `docs.jsonl` produces a
byte-identical `.fapack` (checked twice, sha256 `6742ec4f…`), and re-running the extractor
produces a byte-identical `docs.jsonl` (sha256 `bf5d0149…`).

## Validation results

`validation.log` in full; summary:

* packtool tests: **12/12 pass** (schema, chunking, pack layout, manifest, determinism).
* archive: entries `manifest.json` + `content.sqlite` only, both stored (no compression),
  fixed 1980-01-01 timestamps, `zipfile.testzip()` clean, bytes inside the zip match the
  extracted sqlite.
* manifest: id/version/title/licence/sourceUrls/discovery as above; checksum list
  `SHA256SUMS` matches `content.sqlite`, `manifest.json` and the pack file.
* sqlite: `PRAGMA user_version = 1`, `quick_check = ok`, columns
  `chunk_id, document_id, title, source, text`; 1,944 chunks over 186 documents, 0 empty
  chunks; chunks per document 1 / 10.45 / 131 (max = Appendix B, the practice-test appendix).
* FTS5: for the six manifest example questions, the canonical section is in the top 3 for
  **6 of 6** with a plain bm25 query (`ORDER BY bm25(chunks_fts)`), and the section's own
  title lookup returns it first.

| Question | Query | Expected section | v0.1.0 rank | v1.1.0 rank |
|---|---|---|---|---|
| parameter vs statistic | `"parameter" AND "statistic"` | `is2e-1-1` 1.1 Definitions… | 1 | 1 |
| median of an even count | `median` | `is2e-2-5` 2.5 Measures of the Center | 1 | 1 |
| empirical rule | `"empirical rule"` | `is2e-2-7` 2.7 Measures of the Spread | 1 | 1 |
| z-score | `"z-score"` | `is2e-6-1` 6.1 Standard Normal | 2 | 2 |
| binomial distribution | `"binomial distribution"` | `is2e-4-3` 4.3 Binomial Distribution | 5 | **2** |
| confidence interval | `"confidence interval"` | `is2e-8-1` 8.1 Single Population Mean | 2 | 3 |

  **The v0.1.0 binomial miss, and the fix.** FTS5's `bm25` scores a *phrase* by how often it
  occurs in a row, divided by FTS5's length normalisation (`k1 = 1.2`, `b = 0.75`, no column
  weights). Section 4.3 is 13,208 characters, so its 15 chunks are near the corpus average
  (1,022 chars) and the exact phrase "binomial distribution" occurs in only three of them,
  once each. The competing hits are shorter or denser: `is2e-7-3`'s "Normal Approximation to
  the Binomial" note contains the phrase four times in 1,115 characters, and `is2e-9-3` and
  `is2e-9-practice` repeat it in compact hypothesis-test passages. The section's own title
  was indexed in the `title` column but its tokens were absent from `text`, so the body
  chunks could not outscore them.

  v1.1.0 prefixes each numbered section's body with the book's own page heading
  (`4.3 Binomial Distribution`), which is how the composite pages already carry per-section
  headings. That is the only corpus change: 80 documents, `text` gains exactly
  `<title>\n\n`, no words are added beyond the title strings, and the total grows by 455
  words. `is2e-4-3` now ranks 2 (bm25 −5.900 vs −5.106 before); the confidence-interval
  question moves from rank 2 to rank 3 but stays in the top 3 (the three `is2e-8-*` hits sit
  within 0.077 bm25 points of each other).

  The change is not specific to one question: as a general check, querying each numbered
  section's own title puts the right document at rank 1 for 61/80 sections (was 42/80) and in
  the top 3 for 79/80 (was 72/80). Composite-page retrieval is unchanged.

## Known limitations

1. **Licence is CC BY-NC-SA 4.0, not CC BY 4.0** (evidence above). The pack is labelled with
   the true licence; NC/SA terms apply.
2. **No answer/solution pages.** The book publishes `N-solutions` pages, but in the CNXML
   source the `<solution>` elements for odd-numbered exercises are commented out, so they
   are not in the corpus. Solutions that the book prints inside worked examples are kept.
3. **Appendix H "Tables" has no table values.** In both the CNXML and the PDF, Appendix H
   only lists links to NIST tables (z, t, χ², F). Those values are not in the book, so the
   offline pack cannot carry them. Formula content is present in the 12 Formula Review
   pages and Appendix F.
4. **Generated numbering is absent.** "Example 2.5", "Try It 2.5", "Table 1.9", "Figure 1.2"
   numbers are produced by the web renderer and are not in the source. Worked examples and
   exercises keep their full text, but the labels are not there; cross-references that the
   book prints as a number resolve to the target's kind ("Table", "Figure", "Example",
   "Exercise") or to a section title, never to a number. This is the same convention as the
   repo's Prealgebra extractor.
5. **Figures are text.** A figure contributes `[Image: alt text]` plus its caption; images
   are not embedded (the pack format is text-only).
6. **Math is LaTeX-converted MathML** (`$…$`, `$$…$$`) using
   `tools/packs/extract_openstax_prealgebra.py`'s converter; Greek letters such as ∑, μ, σ
   stay as Unicode inside the LaTeX. Occasionally the converter emits `\text{+}` where the
   book prints a plain `+`.
7. **Composite pages are assembled from per-section blocks.** The CNXML keeps a chapter's
   glossary, review, formula review, practice and homework in each section's module; the
   pack concatenates them in book order, each block headed by the book's own section title.
   No other text is added.
8. **Example questions are capped at 6 by `packtool`** (`build_pack` rejects more), so the
   requested 5–8 became 6.
9. **No PDF page ranges in `source`.** Every document points at its exact web page instead;
   the PDF was downloaded only as a cross-check (its text extraction mangles ligatures such
   as "ffi" and interleaves page headers, so it was not used as an oracle).
10. **A numbered section's heading also appears at the top of its body.** `text` begins with
    the same string as `title`, so a reader that renders both shows it twice. That is
    deliberate: the body then starts the way the book's page starts, and the section title is
    searchable as body text (see "Validation results"). It is the only text added anywhere in
    the corpus, and it is the book's own title.

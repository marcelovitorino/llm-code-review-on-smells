# -*- coding: utf-8 -*-
"""Build a Taguette project file (.sqlite3) from the v04 Misleading coding.

Turns `results/v04_misleading_manual_coding.csv` plus the raw material in Postgres
into a project that can be uploaded at https://app.taguette.org/project/import,
so the coding lives as tagged highlights anchored to evidence instead of CSV cells.

It also writes `results/v04_misleading_codebook.csv`, which Taguette accepts on its
own via "Project info -> Import codebook" (tag list only, no highlights).

Outputs
    results/v04_misleading_taguette_project.sqlite3
    results/v04_misleading_codebook.csv

Requirements
    pip install "taguette==1.5.2" "setuptools<81" psycopg2-binary

The taguette pin must match the server: the import runs alembic on the uploaded
file, and a file stamped NEWER than the server is rejected with "unknown version".
app.taguette.org was running 1.5.2-3-gf706e2e when this was written; the version is
in the page footer.

Offsets follow Taguette's convention: UTF-8 byte offsets over the document's text
nodes, with HTML tags not counted (see taguette/extract.py). Rather than searching
for text, the builder lays each document out as a flat list of top-level elements
and takes offsets from element boundaries, then asserts that Taguette's own
extract() reproduces every stored snippet.

Run from the repository root.
"""
import csv
import html
import json
import os
import re
import sys

import bleach
import bs4
import psycopg2
from sqlalchemy import func

from taguette import convert, database, extract
from taguette.database import models as M

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from start_here.experiments.constants import (  # noqa: E402
    RESULTS_DATABASE_NAME, RESULTS_DATABASE_HOST, RESULTS_DATABASE_PORT,
    RESULTS_DATABASE_USER, RESULTS_DATABASE_PASSWORD,
)
CODING_CSV = os.path.join(REPO, "results", "v04_misleading_manual_coding.csv")
OUT = os.path.join(REPO, "results", "v04_misleading_taguette_project.sqlite3")
CODEBOOK = os.path.join(REPO, "results", "v04_misleading_codebook.csv")

JUDGE = "openai_gpt-4.1-v04@llm.eval"
GENERATION_EXPERIMENT = 3  # the run under test; the judge is experiment 7


def load_items():
    """One row per Misleading item, with the review the judge actually saw.

    evaluation_labels.llm_result_id points at the JUDGE's row, not at the review
    under test, so the review is joined through mlcq_files instead.
    """
    conn = psycopg2.connect(
        dbname=RESULTS_DATABASE_NAME, host=RESULTS_DATABASE_HOST,
        port=RESULTS_DATABASE_PORT, user=RESULTS_DATABASE_USER,
        password=RESULTS_DATABASE_PASSWORD,
    )
    cur = conn.cursor()
    cur.execute(
        """
        SELECT o.id, o.smell, o.severity, o.code_name, o.start_line, o.end_line,
               o.code_snippet, el.comment AS judge_comment,
               rj.prompt AS judge_prompt, r3.response AS review
        FROM evaluation_labels el
        JOIN mlcq_smell_occurrences o ON o.id = el.smell_occurrence_id
        JOIN llm_prompt_results rj ON rj.id = el.llm_result_id
        JOIN mlcq_files f ON o.id = ANY(f.smell_occurrence_ids)
        JOIN llm_prompt_results r3
          ON r3.mlcq_file_id = f.id AND r3.experiment_id = %s
        WHERE el.annotator = %s AND el.label = 'M'
        ORDER BY o.smell, o.id
        """,
        (GENERATION_EXPERIMENT, JUDGE),
    )
    cols = [d[0] for d in cur.description]
    rows = [dict(zip(cols, r)) for r in cur.fetchall()]
    conn.close()
    for r in rows:
        assert (r["review"] or "").strip()[:200] in r["judge_prompt"], (
            "review %s is not the text the judge saw" % r["id"]
        )
    return {int(r["id"]): r for r in rows}


ITEMS = load_items()
CODES = {int(r["occ_id"]): r for r in csv.DictReader(open(CODING_CSV))}
assert set(ITEMS) == set(CODES), "coding CSV and database disagree on the item set"

BLEACH = dict(
    tags={'p','br','code','blockquote','pre','sub','sup','caption','a','img',
          'h1','h2','h3','h4','h5','strong','em','b','u','q','del',
          'ul','ol','li','dl','dt','dd','table','thead','tbody','tr','th','td',
          'colgroup','col'},
    attributes={'a': {'href','title'}, 'img': {'src','width','height'}},
    strip=True,
)
ABBR = {"data class":"DC", "feature envy":"FE", "long method":"LM"}
SMELL_PAT = {
 "data class":  r"data[- ]?class|data holder|data container|anemic|dumb data|pure data|passive data|getters?/?and/? ?setters",
 "feature envy":r"feature envy|move method|belongs (in|to)|more interested in|misplaced|envy",
 "long method": r"long method|long function|lengthy method|monolithic method|doing too much|too long|excessively long|method length",
}
LM_PAT = re.compile(r"long method|long function|lengthy method|monolithic method|doing too much|overly long|too long|multi-responsibility|multiple responsibilities|method length|monolithic|decompos|method complexity|extract method|smaller[^.]{0,25}(?:method|helper)", re.I)

# ---------------------------------------------------------------- document HTML
def blocks_from_text(text):
    """Split markdown-ish text into (kind, text) blocks: 'pre' for fenced code, 'p' otherwise."""
    out, parts = [], re.split(r"(?m)^\s*```.*$", text)
    for i, part in enumerate(parts):
        if i % 2 == 1:                                   # inside a fence
            if part.strip():
                out.append(("pre", part.strip("\n")))
        else:
            for para in re.split(r"\n\s*\n", part):
                para = para.strip("\n")
                if para.strip() and para.strip() != "---":
                    out.append(("p", para))
    return out

def build_doc(item):
    """Return (elements, spans) where elements is a list of (tag, text) and spans maps
    a label to a (first_element_index, last_element_index) inclusive range."""
    els, spans = [], {}
    def add(tag, text):
        els.append((tag, text)); return len(els) - 1

    add("h3", "Annotated sample (oracle granularity)")
    i = add("pre", item["code_snippet"] or "")
    spans["sample"] = (i, i)

    add("h3", "Review under test (gpt-4.1)")
    review = item["review"] or ""
    sections = [s for s in re.split(r"\n\s*-{3,}\s*\n", review) if s.strip()]
    if len(sections) < 2:
        sections = [s for s in re.split(r"\n\s*\n", review) if s.strip()]
    sec_ranges = []
    for sec in sections:
        blocks = blocks_from_text(sec)
        if not blocks:
            continue
        first = len(els)
        for tag, txt in blocks:
            add(tag, txt)
        sec_ranges.append((first, len(els) - 1, sec))

    add("h3", "Judge reasoning (v04)")
    jc = item["judge_comment"] or ""
    mj = re.search(r"JUSTIFICATION\s*:\s*(.*)", jc, re.S)
    head = jc[:mj.start()].rstrip() if mj else jc
    i = add("pre", head)
    if mj:
        j = add("pre", "JUSTIFICATION: " + re.sub(r"\s+", " ", mj.group(1)).strip())
        spans["justification"] = (j, j)
    else:
        spans["justification"] = (i, i)

    # section that argues the target smell
    pat = re.compile(SMELL_PAT[item["smell"]], re.I)
    best = max(sec_ranges, key=lambda sr: len(pat.findall(sr[2])), default=None)
    if best and len(pat.findall(best[2])) > 0:
        spans["smell_section"] = (best[0], best[1])
    elif sec_ranges:
        spans["smell_section"] = (sec_ranges[-1][0], sec_ranges[-1][1])

    # section that pushes Long Method hardest (used only when the code says yes)
    lm = max(sec_ranges, key=lambda sr: len(LM_PAT.findall(sr[2])), default=None)
    if lm and len(LM_PAT.findall(lm[2])) > 0:
        spans["lm_section"] = (lm[0], lm[1])
    return els, spans

def render(els):
    return "".join("<%s>%s</%s>" % (t, html.escape(x, quote=False), t) for t, x in els)

# ------------------------------------------------------------------- offsets
def offsets_of_elements(cleaned_html, n_elements):
    """Byte offset (start, end) of each top-level body element, in Taguette's offset space
    (UTF-8 bytes of text nodes only, tags not counted)."""
    soup = bs4.BeautifulSoup(cleaned_html, "html5lib")
    body = soup.body
    tops = [c for c in body.contents]
    assert len(tops) == n_elements, f"top-level mismatch {len(tops)} != {n_elements}"
    res, pos = [], 0
    for node in tops:
        start = pos
        for s in ([node] if isinstance(node, bs4.NavigableString) else node.find_all(string=True)):
            pos += len(str(s).encode("utf-8"))
        res.append((start, pos))
    return res

# --------------------------------------------------------------------- tags
REASON_TAG = [
 ("reason.constants_holder",      r"constants holder"),
 ("reason.generated_code",        r"generated"),
 ("reason.length_acceptable",     r"length acceptable"),
 ("reason.interface_or_no_fields",r"^interface|no fields|thin subclass|holds no data|purely behavioral"),
 ("reason.legitimate_access",     r"legitimate|delegat|orchestrat|own fields|own state|own children|own dependencies|own parameters|public APIs|not their internals|internals|facade|wrapper|adapter|as needed|appropriate for|test context|core responsibility|local variables"),
 ("reason.not_passive_holder",    r"behavior|invariant|value object|encapsulat|owns |manages|maintains|acknowledged|factory|validation|predicate"),
]
TAG_DESCR = {
 "denial.with_reason":  "Review denies the target smell and gives an explicit argument about the annotated sample.",
 "denial.no_reason":    "Review denies the target smell for the file but gives no argument about the annotated sample.",
 "denial.not_discussed":"Review never engages with the target smell for the annotated sample.",
 "reason.not_passive_holder":     "Ground: the class is said to hold behavior, so it is not a passive data holder.",
 "reason.legitimate_access":      "Ground: access to or delegation towards other classes is said to be legitimate.",
 "reason.interface_or_no_fields": "Ground: the sample is an interface, has no fields, or is a thin subclass.",
 "reason.generated_code":         "Ground: the code is machine generated, so the smell is said not to apply.",
 "reason.constants_holder":       "Ground: a constants holder is an idiomatic Java pattern.",
 "reason.length_acceptable":      "Ground: the method length is said to be acceptable.",
 "long_method_main_issue":"Review promotes a Long Method from the same file as its headline finding.",
 "oracle_inconsistent":   "The annotated sample objectively contradicts the smell the oracle assigned.",
 "judge_error":           "The judge classified M although the review points at the target smell; per the decision tree this should be H.",
}

def reason_tag(reason):
    for name, pat in REASON_TAG:
        if re.search(pat, reason, re.I):
            return name
    raise AssertionError("ungrouped reason: %r" % reason)

# --------------------------------------------------------------------- build
if os.path.exists(OUT):
    os.remove(OUT)
Session = database.connect("sqlite:///" + OUT)
db = Session()

proj = M.Project(
    name="v04 Misleading coding (69 items)",
    description=(
        "Qualitative coding of the 69 Misleading items of the v04 experiment "
        "(LLM code review on code smells, MLCQ oracle). One document per item: annotated "
        "sample, full review produced by the gpt-4.1 under test, and the full reasoning of "
        "the v04 LLM judge. Highlights carry the coding: denial.* on the passage that argues "
        "the target smell, reason.* on the same passage, long_method_main_issue on the passage "
        "that promotes a Long Method, oracle_inconsistent on the annotated sample, judge_error "
        "on the judge's JUSTIFICATION. Generated from results/v04_misleading_manual_coding.csv."
    ),
)
db.add(proj); db.flush()

tags = {}
def tag(path):
    if path not in tags:
        t = M.Tag(project_id=proj.id, path=path, description=TAG_DESCR.get(path, ""))
        db.add(t); db.flush(); tags[path] = t
    return tags[path]
for p in ("denial.with_reason","denial.no_reason","denial.not_discussed",
          "reason.not_passive_holder","reason.legitimate_access","reason.interface_or_no_fields",
          "reason.generated_code","reason.constants_holder","reason.length_acceptable",
          "long_method_main_issue","oracle_inconsistent","judge_error"):
    tag(p)

order = {"data class":0, "feature envy":1, "long method":2}
n_hl = 0
for occ in sorted(ITEMS, key=lambda k: (order[ITEMS[k]["smell"]], k)):
    item, code = ITEMS[occ], CODES[occ]
    els, spans = build_doc(item)
    raw = render(els)
    cleaned = bleach.clean(raw, **BLEACH)
    assert convert.is_html_safe(cleaned), f"unsafe html for {occ}"
    el_off = offsets_of_elements(cleaned, len(els))

    short = item["code_name"].split("#")[0].split(" ")[0].split(".")[-1] or item["code_name"][:20]
    name = f"{occ:05d} {ABBR[item['smell']]} {'crit' if item['severity']=='critical' else 'maj'} {short}"[:50]
    fname = re.sub(r"[^A-Za-z0-9._-]+", "_", f"{occ:05d}_{item['code_name']}")[:95] + ".html"
    doc = M.Document(
        project_id=proj.id, name=name,
        description=(f"smell={item['smell']}; severity={item['severity']}; "
                     f"lines={int(item['end_line'])-int(item['start_line'])+1} "
                     f"({item['start_line']}-{item['end_line']}); code={item['code_name']}"),
        filename=fname, text_direction=M.TextDirection.LEFT_TO_RIGHT, contents=cleaned,
    )
    db.add(doc); db.flush()

    def highlight(span_key, tag_paths):
        global n_hl
        if span_key not in spans or not tag_paths:
            return
        a, b = spans[span_key]
        start, end = el_off[a][0], el_off[b][1]
        if end <= start:
            return
        snip = extract.extract(cleaned, start, end)
        assert convert.is_html_safe(snip), f"unsafe snippet {occ} {span_key}"
        h = M.Highlight(document_id=doc.id, start_offset=start, end_offset=end, snippet=snip)
        db.add(h); db.flush()
        for p in tag_paths:
            db.execute(M.highlight_tags.insert().values(highlight_id=h.id, tag_id=tag(p).id))
        n_hl += 1

    dt = code["author_denial_type"]
    dtags = [f"denial.{dt}"]
    if dt == "with_reason":
        dtags.append(reason_tag(code["author_reason"]))
    highlight("smell_section", dtags)
    if code["author_long_method_main_issue"] == "yes":
        highlight("lm_section", ["long_method_main_issue"])
    if code["author_oracle_inconsistent"].startswith("yes"):
        highlight("sample", ["oracle_inconsistent"])
    if code["author_judge_error"].startswith("yes"):
        highlight("justification", ["judge_error"])

db.commit()

# ----------------------------------------------------------------- verify
docs = db.query(M.Document).count()
hls = db.query(M.Highlight).count()
print(f"written: {OUT}")
print(f"  project: {proj.name!r}")
print(f"  documents: {docs} | tags: {db.query(M.Tag).count()} | highlights: {hls}")
counts = (db.query(M.Tag.path, func.count(M.highlight_tags.c.highlight_id))
            .outerjoin(M.highlight_tags, M.Tag.id == M.highlight_tags.c.tag_id)
            .group_by(M.Tag.path).all())
print("\n  tag counts:")
for p, c in sorted(counts, key=lambda x: (-x[1], x[0])):
    print(f"    {p:<32} {c:>3}")
db.close()
print("\n  size: %.1f KB" % (os.path.getsize(OUT)/1024))


# ------------------------------------------------------- codebook (tags only)
CODEBOOK_ORDER = [
    "denial.with_reason", "denial.no_reason", "denial.not_discussed",
    "reason.not_passive_holder", "reason.legitimate_access",
    "reason.interface_or_no_fields", "reason.generated_code",
    "reason.constants_holder", "reason.length_acceptable",
    "long_method_main_issue", "oracle_inconsistent", "judge_error",
]
with open(CODEBOOK, "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh, lineterminator="\n")
    w.writerow(["tag", "description"])
    for path in CODEBOOK_ORDER:
        w.writerow([path, TAG_DESCR[path]])
print("\n  codebook: %s (%d tags)" % (CODEBOOK, len(CODEBOOK_ORDER)))

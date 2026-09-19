#!/usr/bin/env python3
"""Stdlib-only re-check of mintlify/docs-url-discovery-bench from its committed artifacts.

Usage: python3 recheck.py <path-to-clone-of-docs-url-discovery-bench>

1. Reproduces the published per-agent/arm table (accuracy, 404s per task) from
   data/full/results.jsonl using the repo's own validity rule (rows without an
   `error` key), so no numpy/scipy needed.
2. Checks every `expected` path in dataset/full.json against the committed
   data/full/page-inventory.json (the site's own llms.txt + sitemap).
3. Classifies every incorrect valid attempt by where the agent's answer landed
   relative to the expected page, using the repo's normalize_path.
"""
import collections
import json
import re
import sys
from pathlib import Path

root = Path(sys.argv[1])
sys.path.insert(0, str(root))
from url_discovery_bench.grade import normalize_path  # noqa: E402

rows = [json.loads(l) for l in (root / "data/full/results.jsonl").read_text().splitlines() if l.strip()]
inventory = json.load(open(root / "data/full/page-inventory.json"))
dataset = json.load(open(root / "dataset/full.json"))

valid = [r for r in rows if "error" not in r]
print(f"rows={len(rows)} valid={len(valid)} failed={len(rows) - len(valid)}")

# 1. Headline table
print("\n== 1. Published table, recomputed (n, accuracy %, 404s/task, fetches) ==")
cells = collections.defaultdict(list)
for r in valid:
    cells[(r["agent"], r["arm"])].append(r)
for agent in ("claude", "codex"):
    for arm in ("html", "md", "md-link", "md-inline"):
        rs = cells[(agent, arm)]
        n = len(rs)
        acc = 100 * sum(1 for r in rs if r.get("correct")) / n
        nf = sum(r.get("notFound", 0) for r in rs) / n
        fe = sum(r.get("fetches", 0) for r in rs) / n
        print(f"{agent:6} / {arm:9} n={n:3}  acc={acc:5.1f}  404s/task={nf:4.2f}  fetches={fe:5.1f}")

# 2. Ground truth vs inventory
print("\n== 2. expected paths vs committed page inventory ==")
norm_inv = {site: {normalize_path(p) for p in pages} for site, pages in inventory.items()}
missing = []
n_tasks = 0
for site in dataset["sites"]:
    inv = norm_inv.get(site["name"], set())
    for t in site["tasks"]:
        n_tasks += 1
        exp = t["expected"] if isinstance(t["expected"], list) else [t["expected"]]
        hit = [e for e in exp if normalize_path(e) in inv]
        if not hit:
            missing.append((site["name"], t["id"], exp))
print(f"tasks={n_tasks} sites={len(dataset['sites'])} inventory_sites={len(inventory)}")
print(f"expected paths NOT in the site's inventory: {len(missing)}")
for m in missing:
    print("  ", m)

# 3. Wrong-answer taxonomy
print("\n== 3. Incorrect valid attempts: where did the answer land? ==")
wrong = [r for r in valid if not r.get("correct")]
print(f"incorrect={len(wrong)} of {len(valid)} valid ({100 * len(wrong) / len(valid):.1f}%)")
tax = collections.Counter()
by_task = collections.Counter()
examples = collections.defaultdict(list)
for r in wrong:
    exp = r["expected"] if isinstance(r["expected"], list) else [r["expected"]]
    e0 = normalize_path(exp[0])
    a = r.get("answerUrl")
    inv = norm_inv.get(r["site"], set())
    if r.get("offProxy"):
        k = "off-proxy URL (memorized production host)"
    elif not a:
        k = "no URL in answer"
    else:
        an = normalize_path(a)
        if an == e0:
            k = "BUG? normalizes equal to expected but graded wrong"
        elif an in inv:
            if e0.startswith(an + "/"):
                k = "real page: ancestor of expected"
            elif an.startswith(e0 + "/"):
                k = "real page: descendant of expected"
            elif an.rsplit("/", 1)[0] == e0.rsplit("/", 1)[0]:
                k = "real page: sibling of expected"
            else:
                k = "real page: elsewhere on site"
        else:
            k = "path not in inventory (404 or invented)"
    tax[k] += 1
    by_task[(r["site"], r["task"])] += 1
    if len(examples[k]) < 3:
        examples[k].append((r["site"], r["task"], r["agent"], r["arm"], a, exp[0]))
for k, v in tax.most_common():
    print(f"{v:4}  {k}")
    for ex in examples[k]:
        print("        e.g.", ex)
print("\ntasks with the most wrong attempts (site, task): count")
for (s, t), c in by_task.most_common(8):
    print(f"  {s}/{t}: {c}")

# 3b. Same taxonomy, per arm, collapsed to "real page elsewhere" vs "not a page"
print("\n== 3b. Per arm: wrong answers that are a real page vs not a page ==")
per_arm = collections.defaultdict(collections.Counter)
for r in wrong:
    a = r.get("answerUrl")
    inv = norm_inv.get(r["site"], set())
    if r.get("offProxy") or not a:
        per_arm[r["arm"]]["no usable answer"] += 1
    elif normalize_path(a) in inv:
        per_arm[r["arm"]]["real page, wrong one"] += 1
    else:
        per_arm[r["arm"]]["not a page"] += 1
for arm in ("html", "md", "md-link", "md-inline"):
    c = per_arm[arm]
    print(f"{arm:9} total={sum(c.values()):3}  " + "  ".join(f"{k}={v}" for k, v in c.items()))

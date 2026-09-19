# docs-url-discovery-bench: Tier 0 reproduction + wrong-answer taxonomy (2026-09-18)

Target: [mintlify/docs-url-discovery-bench](https://github.com/mintlify/docs-url-discovery-bench) at `5f055a8` (2026-07-14), the benchmark behind the "llms.txt removes ~90% of agent 404s" finding. Everything below is computed from the artifacts committed in that repo (`data/full/results.jsonl`, `data/full/page-inventory.json`, `dataset/full.json`) with `recheck.py`, Python 3 stdlib only, no API keys, no model calls. The repo's own `normalize_path` is imported for grading parity. Full output: `recheck-output.txt`.

## 1. The published table reproduces exactly

2,672 rows; 2,400 valid (no `error` key), 272 failed, matching RESULTS.md's "Attempts and exclusions".

| agent / arm | n | accuracy % (mine / published) | 404s per task (mine / published) | fetches |
|---|---|---|---|---|
| claude / html | 300 | 96.0 / 96.0 | 1.12 / 1.1 | 6.7 |
| claude / md | 300 | 94.3 / 94.3 | 0.79 / 0.8 | 7.0 |
| claude / md-link | 300 | 97.3 / 97.3 | 0.10 / 0.1 | 4.1 |
| claude / md-inline | 300 | 99.0 / 99.0 | 0.02 / 0.0 | 4.6 |
| codex / html | 300 | 97.7 / 97.7 | 3.33 / 3.3 | 26.5 |
| codex / md | 300 | 96.0 / 96.0 | 2.05 / 2.0 | 24.9 |
| codex / md-link | 300 | 97.7 / 97.7 | 0.15 / 0.2 | 13.2 |
| codex / md-inline | 300 | 99.3 / 99.3 | 0.18 / 0.2 | 10.8 |

Every cell matches RESULTS.md ("Full table") to the published precision. The 404 reduction html -> md-link is 91% (Claude) and 95% (Codex) on these numbers.

## 2. Where the 68 wrong answers land (exact-path grading)

68 of 2,400 valid attempts are graded incorrect (2.8%). Classified against each site's committed page inventory (llms.txt + sitemap) after the repo's own normalization:

| class | attempts |
|---|---|
| real page on the site, elsewhere | 40 |
| real page on the site, sibling of expected | 13 |
| no URL in the answer | 12 |
| path not in inventory (404 or invented) | 3 |

So 53 of 68 (78%) wrong answers are a real page; agents almost never invent a URL. Five questions account for 44 of the 68 (65%):

| site / task | n | correct | dominant wrong answer |
|---|---|---|---|
| cartesia / cartesia-brand-name-speech | 24 | 13 | `/build-with-cartesia/capability-guides/specify-custom-pronunciations` x9 (expected `.../custom-pronunciations`) |
| stytch / stytch-migrate-m2m-from-auth0 | 24 | 14 | `/docs/multi-tenant-auth/authentication/m2m/import-clients` x10 (expected `/docs/consumer-auth/...`) |
| lago / lago-price-one-metric-by-region | 24 | 15 | `/guide/plans/charges/charges-with-filters` x7 (expected `/guide/billable-metrics/filters`) |
| stytch / stytch-support-login-as-user | 24 | 17 | `/docs/multi-tenant-auth/authentication/user-impersonation` x7 |
| stytch / stytch-instant-logout-jwt-caveat | 24 | 17 | `/docs/consumer-auth/manage-sessions/jwts-and-tokens` x3, no URL x3 |

Two patterns:

- **Product twins (Stytch).** 19 wrong attempts across the Stytch tasks answered the `multi-tenant-auth` (B2B) page whose path is identical to the expected `consumer-auth` (B2C) page except for the product segment. None of the three questions says which product. Under exact-path grading these count as misses.
- **Alias slug (Cartesia).** 9 attempts answered `specify-custom-pronunciations`; both slugs are in the July inventory, only `custom-pronunciations` is in today's `llms.txt`. I could not confirm today that the two served the same page (the old slug now returns 429 and redirects to a login page), so this one is "likely a rename", not verified.

If the Stytch twins and the Cartesia alias are accepted as correct, overall accuracy moves from 2332/2400 = 97.2% to 2360/2400 = 98.3% (+28 attempts). This does not change the 404 finding at all; it only says the accuracy column understates the agents a little, and that the `expected` field (which already supports a list) could carry the twin paths.

## 3. One `expected` path has moved since the run

`aptible / aptible-restrict-llms-per-env` expects `/docs/ai-gateway/model-access-policies.md`. That path is not in the committed Aptible inventory, which lists `/docs/llm-gateway/model-access-policies`. Live check on 2026-09-18: `https://www.aptible.com/docs/ai-gateway/model-access-policies` returns 301 -> `/docs/llm-gateway/model-access-policies` (200), and Aptible's `llms.txt` lists only the `llm-gateway` path. All 24 July attempts were graded correct (the old path was live then). Anyone running Tier 1/2 on this dataset today will be steered to the new path by `llms.txt` and graded 0/24 on that task, because `normalize_path` compares strings and does not follow redirects. Fix: make `expected` a list with both paths (schema already allows it).

## Re-verification (2026-09-18, second run)

Upstream `main` is still `5f055a8`; `recheck.py` against a fresh clone produces output byte-identical to `recheck-output.txt`. No issue or PR on the upstream covers the twins or the Aptible path (11 items total, all PRs; PR #4 added a general exact-path grading caveat to the docs, none reports these cases). The old Aptible path now answers `308` (permanent redirect) rather than `301`, same target `/docs/llm-gateway/model-access-policies`; Aptible's `llms.txt` still lists only the `llm-gateway` path. The conclusion in section 3 is unchanged.

## How to rerun

```
git clone https://github.com/mintlify/docs-url-discovery-bench
python3 recheck.py docs-url-discovery-bench        # ~1 s, stdlib only
```

Live checks used plain `curl -L` on the four URLs named above.

## Limitations

- Sections 2 and 3 are my reading of committed data plus two live HTTP checks; whether a "twin" page actually answers the question is a judgment the dataset authors should make, and I did not re-run any agent.
- The Cartesia alias is unverified today (rate limited / login redirect on the old slug).
- `numpy`/`scipy` were not available in my environment, so I did not regenerate the site-clustered significance tests in `analysis/stats.py`; nothing here touches them.

## Exact-path grading: 28 of 68 wrong answers are twin/alias pages; one `expected` path has moved

I re-derived the RESULTS.md table from `data/full/results.jsonl` with a stdlib script (all 8 cells match) and then classified the 68 incorrect valid attempts against `data/full/page-inventory.json` using your `normalize_path`. Script and full output: https://github.com/vsahasi/url-discovery-bench-recheck

**53 of 68 wrong answers are a real page on the site** (40 elsewhere, 13 siblings); 12 had no URL in the answer; only 3 were paths not in the inventory. Five questions account for 44 of the 68:

| site / task | wrong | dominant wrong answer |
|---|---|---|
| cartesia / cartesia-brand-name-speech | 11 | `.../specify-custom-pronunciations` x9 (expected `.../custom-pronunciations`) |
| stytch / stytch-migrate-m2m-from-auth0 | 10 | `/docs/multi-tenant-auth/authentication/m2m/import-clients` x10 |
| lago / lago-price-one-metric-by-region | 9 | `/guide/plans/charges/charges-with-filters` x7 |
| stytch / stytch-support-login-as-user | 7 | `/docs/multi-tenant-auth/authentication/user-impersonation` x7 |
| stytch / stytch-instant-logout-jwt-caveat | 7 | `.../jwts-and-tokens` x3, no URL x3 |

1. **Stytch product twins (19 attempts).** The three Stytch questions do not say consumer vs B2B, and the `multi-tenant-auth` page has the same path as the expected `consumer-auth` page apart from the product segment. If the twin is an acceptable answer, `expected` (already list-typed) could carry both.
2. **Cartesia alias (9 attempts).** Both `custom-pronunciations` and `specify-custom-pronunciations` are in the July inventory; only the former is in today's `llms.txt`. I could not verify today that they served the same content (the old slug now redirects to a login page), so treat this as "probably a rename".
3. **Aptible expected path moved.** `aptible-restrict-llms-per-env` expects `/docs/ai-gateway/model-access-policies.md`, which is not in the committed inventory; the live URL now permanently redirects (301 on first check, 308 on re-check) to `/docs/llm-gateway/model-access-policies`, and Aptible's `llms.txt` lists only the new path. All 24 July attempts were graded correct, but a Tier 1/2 re-run today would grade 0/24 on that task because `normalize_path` compares strings. Suggest `expected: ["/docs/ai-gateway/model-access-policies", "/docs/llm-gateway/model-access-policies"]`.

Accepting 1 and 2 moves overall accuracy from 2332/2400 (97.2%) to 2360/2400 (98.3%). None of this touches the 404 result, which is what the paper is about; it is only that the accuracy column is a bit conservative and the dataset will drift under exact-path grading.

Happy to send a PR for the Aptible entry and, if you agree on the twins, the Stytch/Cartesia lists.

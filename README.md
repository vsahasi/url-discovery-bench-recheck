# url-discovery-bench recheck

A stdlib-only re-check of [mintlify/docs-url-discovery-bench](https://github.com/mintlify/docs-url-discovery-bench) from its committed artifacts.

- The published accuracy and 404s-per-task table reproduces exactly (8/8 cells).
- Of the 68 graded-wrong attempts, 53 are a real page on the site; 5 questions account for 44 of them. 19 are the Stytch B2B twin of the expected B2C page; 9 are a Cartesia alias slug. Accepting those moves accuracy from 97.2% to 98.3%.
- One `expected` path (Aptible) now 301-redirects; a re-run today would grade that task 0/24 under exact-path matching.

Files: `recheck.py` (run it against a clone of the repo), `recheck-output.txt`, `results.md` (numbers, method, limitations), `ISSUE.md` (issue text for the upstream repo).

Veer Sahasi, 2026-09-18.

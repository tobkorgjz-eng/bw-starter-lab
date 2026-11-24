## W7 review: PR #9 (scribe skeletons), head `93f7686`

**Checks**
- Docs only, no tests to run (the branch passes in the all-PR merge run: 10 folders, 206 tests, offline).
- Secrets/tokens: none. The `sreq_...` request ID in `FEEDBACK/w8-scribe.md:25` is an ID, not a credential, so it is fine. Wording: none.

**Findings** (all small, for when you fill the docs)

1. `docs/factory-recipe.md:28,36` point to `docs/prompts/`, which does not exist on any branch yet. *Fix:* when filling, either have the manager add `docs/prompts/` or copy the prompts in directly.
2. `docs/factory-recipe.md:12-20` PR column: the numbers are now known. w1 → #7, w2 → #6, w3 → #1, w4 → #5, w5 → #2, w6 → #4 (supersedes #3), w7 → #8, w8 → #9.
3. `FEEDBACK/w8-scribe.md` still has a few "(to update)" and "(to fill)" placeholders. Fill them or remove them before asking for a merge.

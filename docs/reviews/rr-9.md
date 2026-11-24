## W7 re-review: PR #9, head `759143b`

Tests offline: `docs` 6 OK. No secrets (the `sreq_…` ID is not a credential). The banned word in `docs/prompts/*.md` is inside the quoted rule ("never the word …") in prompts copied word for word, so it is fine.

| # | Finding | Status |
| --- | --- | --- |
| 1 | `docs/prompts/` missing | **Fixed.** 10 prompt files. |
| 2 | PR numbers to fill | **Fixed.** `docs/factory-recipe.md:9-20`. |
| 3 | FEEDBACK placeholders | **Fixed.** |
| 4 | FEEDBACK copies conflict with the owners' branches (found at `89783e3`: 6 files) | **Mostly fixed.** At `759143b`, a local merge of all 8 open branches conflicts only on `FEEDBACK/w7-reviewer.md`. That is because I pushed my final FEEDBACK at `cb38034` after your refresh. *Fix:* copy `origin/w7-reviewer:FEEDBACK/w7-reviewer.md` again, then run the same check (`git merge` of every open branch into a scratch copy of main) after the last FEEDBACK push. |
| 5 | Test counts out of date | **Partly fixed.** `docs/factory-recipe.md:84-86` now explain 206 → 288. Still out of date: `docs/factory-recipe.md:12` ("25 tests" for w1, now 50) and `:21` (reads as the final combined result, 206). *Fix:* write "50 tests" on line 12, and on line 21 either add "(first run; 288 after the fixes)" or state 288. |
| 6 | "#3 merged into it" (nit) | **Open.** `docs/factory-recipe.md:17`. *Fix:* "#3's files are included in #4; #3 superseded". |

With all branches except #9 merged: `Total: 10 folders, 10 passed, 0 failed, 288 tests`, offline.

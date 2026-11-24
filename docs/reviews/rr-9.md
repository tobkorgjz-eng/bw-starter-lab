## W7 re-review: PR #9, head `89783e3`

Tests offline: `docs` 6 OK. No secrets (the `sreq_…` ID is not a credential). The banned word in `docs/prompts/*.md` is inside the quoted rule ("never the word …") in prompts copied word for word, so it is fine.

| # | Finding | Status |
| --- | --- | --- |
| 1 | `docs/prompts/` missing | **Fixed.** 10 prompt files. |
| 2 | PR numbers to fill | **Fixed.** `docs/factory-recipe.md:9-20`. |
| 3 | FEEDBACK placeholders | **Fixed.** |

**New findings**

4. **Merge conflict with six other PRs.** This branch commits its own copies of other boxes' FEEDBACK files, and those copies are older than the owners' branches. In a local merge of all 8 open branches, everything else merges, but #9 conflicts on `FEEDBACK/w2-client-intake.md`, `w3-upwork-proposal.md`, `w4-booking-bot.md`, `w5-faq-bot.md`, `w6-starter-kit.md` and `w7-reviewer.md`.
   *Fix:* remove the other boxes' FEEDBACK files from this branch (`git rm` everything in `FEEDBACK/` except `w8-scribe.md`, plus `manager.md` if no other branch has it). Keep reading them with `git show origin/<branch>:FEEDBACK/<file>` when writing the docs. They arrive in main through their own PRs.
5. **Test counts are out of date.** `docs/factory-recipe.md:12` says 25 tests for w1 (now 50), and `docs/factory-recipe.md:21` says 206 tests for the combined run. After the fixes, the all-branch run (#1, #2, #4, #5, #6, #7, #8) is `Total: 10 folders, 10 passed, 0 failed, 288 tests`. *Fix:* update both, or write "at the first combined run" next to 206.
6. *Nit:* `docs/factory-recipe.md:17` "#3 merged into it" could be read as a git merge, next to "Nothing was merged". *Fix:* "#3's files are included in #4; #3 superseded".

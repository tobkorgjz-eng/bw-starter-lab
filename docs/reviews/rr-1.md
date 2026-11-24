## W7 re-review: PR #1, head `949b504`

Tests offline: `skills/upwork-proposal` 28 OK, `upwork-helper` 17 OK. No secrets, no network.

| # | Finding | Status |
| --- | --- | --- |
| 1 | Job post not treated as data | **Fixed.** `SKILL.md:29` hard rule 7. My planted-instruction post now scores 1/5 with "treated as data, not followed", and the draft starts with a NOTE. |
| 2 | Any budget "works" | **Fixed.** `proposal.py:143-154` `budget_fits`: $5 now gets "Could we first agree on the scope?…", $800 gets "within our usual range…; we will confirm once the scope is agreed". |
| 3 | Title quoted unchecked | **Fixed.** The injected title is not quoted ("Thanks for your post."). |
| 4 | Old helper claims "good match" at 0/100 | **Fixed.** Neutral "I read your post." plus a low-score NOTE. |
| 5 | Old helper misses title flags / echoes description | **Fixed.** "urgent asap" from the title is flagged, injection phrases are flagged, and the description is no longer quoted ("write this in your own words"). |
| 6 | Banned word in prose (nit) | **Fixed** in `SKILL.md` and `FEEDBACK/w3-upwork-proposal.md`. |

All findings fixed. Note for #9: the scribe's copy of `FEEDBACK/w3-upwork-proposal.md` is the old one.

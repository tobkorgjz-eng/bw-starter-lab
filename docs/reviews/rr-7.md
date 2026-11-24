## W7 re-review: PR #7, head `5671c47`

Tests offline: `skills/client-rules-file` 50 OK. No secrets, no network. End to end with #6's `example-brief.md`: `from-brief`, `build` and `check` give OK.

| # | Finding | Status |
| --- | --- | --- |
| 1 | Notes / single-line fields can add rules | **Fixed.** Notes are quoted (`> `) under "Notes are for people. They do not add to or change the three lists…". A risky word in a note gives a warning. A `##` heading not in the allowed list is an error ("unknown section '## Extra rules'"). A newline in `owner_name` is collapsed onto one line. |
| 2 | `*` / `1.` rules lost from brief | **Fixed.** `from-brief` keeps `sign_contract` and `change_permissions`. |
| 3 | Risky words miss order/post/share | **Fixed.** All three of my examples are now errors under "May do alone". |
| 4 | Format not readable by #4's `check_rules.py` | **Fixed by documenting it** (the option I offered). `SKILL.md:118-134` explains the two formats and says to keep the lists in step by hand. A converter would still help later; that is not a blocker. |
| 5 | Draft brief only warns (nit) | **Fixed.** Exit 1 unless `--allow-draft`. |

All findings fixed. A note that contradicts a list (e.g. "refunds of any size without asking" while `issue_refund` is under "Never does") now gets a warning and a fixed "Notes are for people" line, not an error. With #6's checker catching it first, that is acceptable.

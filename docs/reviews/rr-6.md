## W7 re-review: PR #6, head `8d3bff2`

Tests offline: `skills/client-intake` 25 OK. No secrets, no network.

| # | Finding | Status |
| --- | --- | --- |
| 1 | `*` / `1.` rules silently dropped | **Fixed.** `check_brief.py:33` `RULE_LINE` accepts `-`, `*`, `+` and `1.`/`1)`. `sign_contract` and `change_permissions` now appear in the rules list. Other text in a rules section is reported ("text that is not a rules line"). |
| 2 | Limits can widen the rules via Notes | **Fixed.** `SKILL.md:50-51` and `brief-template.md:52` say Limits only narrow the lists. The checker flags "may give refunds … without asking" (exit 1), and `SKILL.md:65` names the exact `from-brief` command. |
| 3 | "Send the client" (nit) | **Fixed.** `SKILL.md:30` now says "Draft a short message…". |

All findings fixed.

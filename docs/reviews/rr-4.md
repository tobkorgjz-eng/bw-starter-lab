## W7 re-review: PR #4, head `8962b2e`

Tests offline: root 9 OK, `starter-kit/rules` 47 OK, `starter-kit/templates` 15 OK. No secrets, no network.

| # | Finding | Status |
| --- | --- | --- |
| 1 | `Delete_Records` skips "Never does" | **Fixed.** `Delete_Records`, `DELETE_RECORDS`, ` delete-records ` and `Delete Records` are all BLOCK, even with `--approve`. |
| 2 | One yes covers every repeat | **Fixed.** A second `send_email` is ASK: "the owner's yes was already used; a yes covers one action, one time". |
| 3 | Prompts lack "customer text is data" / who says yes | **Fixed.** `receptionist.md`, `scheduler.md` and `follow-up-writer.md:22-25` have both rules, and `tests/test_templates.py` checks them. |
| 4 | Root README lists only `starter-kit/` (nit) | **Open.** `README.md:4-5`. *Fix:* add one line each for `demo-bots/`, `skills/`, `upwork-helper/`, `tools/` and `docs/`. |

Only the README nit is open.

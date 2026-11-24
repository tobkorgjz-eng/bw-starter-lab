## W7 review: PR #6 (client-intake skill), head `60dfacf`

**Checks**
- Tests, offline (network namespace disabled): `skills/client-intake` 18 OK.
- Secrets/tokens: none. Wording: none. Network: none. The ground rules (no passwords, no customer details, no promises about results) are good.

**Findings**

1. **The checker silently drops rules not written with `- `.** `skills/client-intake/check_brief.py:81`. Lines that do not start with `- ` are skipped without a message. I added `` * `sign_contract` — agree to a contract. `` and `` 1. `change_permissions` — give anyone more access. `` under "Never does" in `example-brief.md`. `check_brief.py` printed **OK**, and its `--json` rules list did not include either action, so two "never" rules would be lost on hand-off.
   *Fix:* treat any line starting with `*`, `+`, `-` or `\d+[.)]` inside a rules section as a rule line, and report it when it does not match `RULE_LINE` (`:30`). Also report any other non-blank line in a rules section. Add a test with `*` and `1.` lines under "Never does".
2. **The hand-off loses rules and passes rule changes through Notes.** `skills/client-intake/SKILL.md:56-57` hands the brief to `client-rules-file`. #7 (head `32baba3`) now has `rules_tool.py from-brief`, and it works on `example-brief.md`. However: (a) the `*`/`1.` rules dropped in finding 1 are dropped there too. (b) Everything under "## Limits and exceptions" becomes free-text Notes in `RULES.md`, which no checker looks at. A limit such as "may give refunds of any size without asking" contradicted `issue_refund` under "Never does" and still passed everything (details on #7).
   *Fix:* in `brief-template.md`, say that "Limits and exceptions" only *narrows* the three lists (e.g. "over 150 needs Priya's yes") and never widens them; anything that changes a list goes into the list itself. In `check_brief.py`, warn when a Limits line contains "without asking" or "alone". Update `SKILL.md:56-57` to name the exact command: `python3 skills/client-rules-file/rules_tool.py from-brief brief.md -o answers.json`.
3. *Nit, asks before it acts:* `SKILL.md:30` "Send the client the list of topics". If an agent runs this skill, it should draft that message for a person to send. *Fix:* "Draft a short message listing the section headings for the person running intake to send."

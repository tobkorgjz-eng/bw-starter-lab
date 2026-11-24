# starter-kit/rules

House rules for a client AI assistant team: **runs by your rules, asks before it acts**.

- `RULES.md` — what the assistant may do alone, what needs the owner's yes,
  and what it never does (example: a made-up bakery). Unlisted actions need a yes.
- `check_rules.py` — checks a bot's planned action list against `RULES.md`.
- `example_plan.json` — a sample plan.
- `test_check_rules.py` — unittest tests.

Python 3 standard library only, no network calls.

```sh
python3 check_rules.py example_plan.json     # exit 0 = all allowed, 1 = ask/block, 2 = bad input
python3 -m unittest                          # run tests (from this folder)
```

A plan is a JSON list of action names or objects such as
`{"action": "send_email", "owner_approved": true}`. "Never does" actions are
blocked even when approved.

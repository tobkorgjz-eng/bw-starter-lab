# starter-kit/rules

House rules for a client AI assistant team: **runs by your rules, asks before it acts**.

- `RULES.md` — what the assistant may do alone, what needs the owner's yes,
  and what it never does (example: a made-up bakery). Unlisted actions need a yes.
- `check_rules.py` — checks a bot's planned action list against `RULES.md`.
- `example_plan.json` — a sample plan written by the bot.
- `example_owner_approvals.json` — a sample list of actions the owner said yes to.
- `test_check_rules.py` — unittest tests.

Python 3 standard library only, no network calls.

```sh
python3 check_rules.py example_plan.json                     # no owner yes given
python3 check_rules.py example_plan.json \
    --approvals example_owner_approvals.json                 # owner's yes from a file
python3 check_rules.py example_plan.json --approve send_email  # owner's yes on the command line
python3 -m unittest                                          # run tests (from this folder)
```

Exit code: 0 = all allowed, 1 = something needs a yes or is blocked, 2 = bad input.

A plan is a JSON list of action names or objects such as `{"action": "send_email"}`.

**The bot cannot approve itself.** The owner's yes comes only from outside the
plan, through `--approvals FILE` (a JSON list of action names) or
`--approve ACTION`. An `owner_approved` (or `approved` / `approval`) field
inside the plan is ignored, so the action still gets ASK, and the output notes
that the in-plan approval was ignored. "Never does" actions stay blocked even
when the owner approves them.

**A yes covers one action, one time.** Each `--approve ACTION`, and each entry
in the approvals file, allows one occurrence of that action in the plan. Give
it twice to allow two. Action names are compared without regard to case,
spaces or `-` versus `_`, so `Delete-Records` is still `delete_records`
(BLOCK).

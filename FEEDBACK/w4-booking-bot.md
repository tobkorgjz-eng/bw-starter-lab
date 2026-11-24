# Feedback: w4-booking-bot

Task: finish demo-bots/booking/ on the existing PR #5 (branch
w3-demo-bots-booking): self-contained demo.html, "asks before it acts",
prompt-injection resistance, tests, accurate README.

## What Discobox did well
- `git fetch origin` worked straight away; the existing branch checked out
  cleanly and its 21 tests already passed.
- `discobox-access request --json ... --wait` was simple: one request with
  three narrow routes (git on this repo, GET on this repo's API, POST comments
  on PR #5). It was approved by the manager within a few minutes and
  `discobox-access list` showed the grant and its expiry.
- `node` was already in the box, so demo.html's script could be run offline
  and its replies compared with booking.py, with no install.

## What got in the way
- Nothing blocking. Small things:
  - The access request was run in the background; the JSON answer was only
    readable from the redirected file after the notification, which is fine
    but easy to miss.
  - My own test bug, not Discobox: a regex expected `var NO = [` but the
    page declares `var YES = [...], NO = [...]` on one line. Error text:
    `json.decoder.JSONDecodeError: Extra data: line 1 column 34 (char 33)`

## Rough time per part
- Reading the branch, rules check, git identity: ~3 min
- Access request and waiting for approval (in parallel with coding): ~5 min
- booking.py safeguards (name rule, injection tripwire, exact yes): ~8 min
- demo.html rewrite (testable core, same replies as Python): ~12 min
- Tests (test_safety.py, test_demo_html.py) and fixing the regex: ~10 min
- README, commit, push, PR comment, this file: ~8 min

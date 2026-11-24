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
- The first granted GitHub credential (request sreq_x2r7edg7ayjgec8h,
  shown by `discobox-access list` as `github (GH_TOKEN -> github.com,
  api.github.com)`) was rejected by GitHub itself. The egress did not block
  anything (audit showed plain 401s, `blocked: false`). Exact errors:
  - plain `git push`: `fatal: could not read Username for 'https://github.com': No such device or address`
    (expected: git has no helper until one is given)
  - `git push` with a credential helper reading `$GH_TOKEN`:
    `remote: Invalid username or token. Password authentication is not supported for Git operations.`
    `fatal: Authentication failed for 'https://github.com/tobkorgjz-eng/bw-starter-lab.git/'`
  - `GET https://api.github.com/repos/tobkorgjz-eng/bw-starter-lab/pulls/5`
    with `Authorization: Bearer $GH_TOKEN`: HTTP `401`, body
    `{"message": "Bad credentials", "documentation_url": "https://docs.github.com/rest", "status": "401"}`
  The manager could not be reached as a session (`ListAgents`: "No reachable
  agents"), so I sent a second access request (sreq_qzw57qjbw070k7c5)
  explaining the 401. The manager denied it as a duplicate and explained the
  cause: the project's GitHub secret itself is rejected by GitHub ("Bad
  credentials") for every box, the manager included, so a re-approval cannot
  fix it. The first approval stays in place; commits stay local until a
  person updates the secret. Lesson: a 401 that is not `blocked` in the
  audit means the secret is bad, not the routes; ask the manager rather
  than re-requesting.
- Small things:
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
- README, commit, this file: ~6 min
- Diagnosing the 401 (audit, API check, second request): ~6 min
- Review round (W7 nits: cancel needs name, word-boundary matching), code,
  tests, README, push, comment: ~15 min. Pushing with the existing approval
  worked first time once the secret was fixed; no new request was needed.

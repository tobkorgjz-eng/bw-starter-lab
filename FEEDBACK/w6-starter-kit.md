# FEEDBACK – w6-starter-kit

## What Discobox did well
- `git fetch origin` worked on the public repo with no credential, so all
  five open PR branches were available straight away.
- Merging PR #3's branch into PR #4's branch was clean (no conflicts).
- `git archive` of the other worker branches into the scratchpad let
  `run_tests.py` be checked against folder layouts it was not written for
  (demo-bots/booking, demo-bots/faq, upwork-helper/tests) without changing
  this branch. All passed (50 tests).
- `discobox-access request` with a narrow route list (push to this repo,
  GET on this repo, POST comments on issues 3 and 4 only) was easy to write.

## What got in the way
- The tool shell's working directory moved after a `cd` inside a compound
  command, so a later relative `cd starter-kit` failed. Exact error text:
  `(eval):cd:1: no such file or directory: starter-kit`
- A multi-step file-edit script failed half-way because a new folder did
  not exist yet; the first half of the edits had already been written. Exact
  error text: `FileNotFoundError: [Errno 2] No such file or directory: 'new-client-layout/rules/README.md'`
  (my mistake, not Discobox's; fixed by creating the folder and running the
  rest).
- The GitHub access request was granted (status `granted`, 2 hours), and the
  egress forwarded the requests (nothing BLOCKED in `discobox-access audit`),
  but GitHub refused the credential itself, so nothing could be pushed or
  commented. Exact error text:
  - `git push`: `remote: Invalid username or token. Password authentication is not supported for Git operations.`
    then `fatal: Authentication failed for 'https://github.com/tobkorgjz-eng/bw-starter-lab.git/'`
  - REST `GET /repos/tobkorgjz-eng/bw-starter-lab/pulls/4`: HTTP 401, `"message": "Bad credentials"`
  The manager confirmed this is the project's GitHub secret itself (it fails
  for every box, manager included), not the routes; no second access request
  was sent. Work was committed locally while waiting for a person to update it.

## Rough time per part
- Fetch, identity check, checkout, merge #3 into #4: ~3 min
- Reading both halves of the pack: ~4 min
- run_tests.py and its tests: ~10 min
- Checking run_tests.py against other branches' layouts: ~2 min
- Tidying the pack (prompts → RULES.md, layout rules/ folder, checklist,
  client README, starter-kit README, root README): ~8 min
- Access request: ~1 min to write; answered by the manager in a few minutes
  (granted, 2 hours, routes as asked)
- Push and PR comments: ~5 min spent finding out why pushing failed (401 from GitHub); not done
- FEEDBACK file: ~3 min

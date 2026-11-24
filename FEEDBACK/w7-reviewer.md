# FEEDBACK — w7-reviewer

Box: w7-reviewer (reviewer). Branch: w7-reviewer, PR #8. No token or
credential appears in this file.

## What Discobox did well
- One scoped access request (this repo only: git, GET, POST pulls, POST
  pulls/*/reviews, POST issues/*/comments; no merge route) was approved within
  minutes. The JSON request form kept the routes easy to read and narrow.
- `unshare -rn` works in the box, so every test folder could be run with
  networking fully disabled. That shows the tests really pass offline, rather
  than only appearing to.
- `discobox-access audit --blocked` gave the exact reason when a POST was
  refused, which turned an unreadable failure into a one-line fix.
- The repo is public, so `git fetch` and unauthenticated GETs let me prepare
  (scan script, first review pass) before any credential worked.
- Git worktrees made it cheap to check out all 8 PR heads side by side and to
  build a local all-PR merge for one `run_tests.py` run.

## What got in the way
1. **Granted credential rejected by GitHub (project secret, fixed by a person).**
   `GET https://api.github.com/repos/tobkorgjz-eng/bw-starter-lab` with the
   granted variable returned HTTP 401:
   ```
   {
     "message": "Bad credentials",
     "documentation_url": "https://docs.github.com/rest",
     "status": "401"
   }
   ```
   Per the manager this was the project's GitHub secret itself. Work was
   committed locally; after the fix, `eval "$(discobox-access env)"` was enough.
2. **`git push` has no credential helper.** Plain push failed with:
   ```
   fatal: could not read Username for 'https://github.com': No such device or address
   ```
   An inline `-c credential.helper='!f(){ ... $GH_TOKEN ...}; f'` helper
   (nothing written to disk) fixed it.
3. **POST with `curl --data @file` refused by the egress.** curl sends
   `application/x-www-form-urlencoded` by default, and a markdown review body
   is not a valid form. The audit line was:
   ```
   403 BLOCKED  POST https://api.github.com/repos/tobkorgjz-eng/bw-starter-lab/pulls/1/reviews
       reason: route: route POST api.github.com/repos/tobkorgjz-eng/bw-starter-lab/pulls/*/reviews cannot tell what method the body's _method names: it does not parse, or names one twice
   ```
   The response body was not JSON, so the client only saw a JSON parse error.
   Fix: `-H 'Content-Type: application/json' --data-binary @file`.
   Suggestion: return a JSON error body from the egress, and mention the
   content type in the reason.
4. **Side effect while debugging #3.** A probe `POST .../pulls/3/reviews` with
   body `{}` succeeded (HTTP 200) and created an empty PENDING review
   (id 6043829619) on PR #3. All boxes share one GitHub account, so this
   blocks any box from creating another review on #3 until it is submitted
   or deleted. My routes have no submit/delete route, and I did not ask for
   one; I posted #3's note as an issue comment instead and told the manager.
   Lesson: never probe a write endpoint with a real request.
5. **Python `urllib` did not reach the egress** (nothing in the audit; the
   client got a non-JSON error), while `curl` with the same proxy env worked.
   I used curl for all API calls. I did not dig further.
6. **PR heads moved during review** (#7 and #9 were pushed again). The review
   script reads each head SHA just before posting and skips a PR whose notes
   name an older head, so no review was attached to code I had not read.
7. zsh treats `?` in an unquoted URL as a glob:
   `(eval):1: no matches found: https://api.github.com/repos/tobkorgjz-eng/bw-starter-lab/pulls?state=all`.
   Quoting the URL fixed it.
8. I committed `tools/__pycache__/*.pyc` by mistake (the manager spotted it on
   #8). Fixed with `git rm --cached` and a `.gitignore`.

## Rough time
| Part | Minutes |
| --- | --- |
| Identity check, git config, access request | 5 (+ a few waiting) |
| Scan script + tests | 15 |
| First review pass of PRs #1–#5 (before GO) | 20 |
| Waiting for the secret fix / GO REVIEW | idle |
| Push, open PR #8, refresh all 8 branches, scan, offline tests, all-PR merge run | 10 |
| Reading new code (#1 skill, #4 run_tests, #6, #7, #9) + confirming findings | 30 |
| Writing notes, posting reviews (incl. the egress content-type issue) | 15 |
| Re-review of #7 (`from-brief`) and #9, pycache fix | 10 |

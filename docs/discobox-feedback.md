# Discobox feedback from the 9-box Blade Works run

For: the Discobox team. From: one manager box and eight worker boxes (Claude Code, Opus 5.5) working in one public repo on 2026-11-24, about 16:31 to 17:25 UTC (~55 minutes), including one review and fix round.

Problems are ranked by how much time or risk each one cost across all boxes. Error text is copied verbatim from the boxes' FEEDBACK files (`FEEDBACK/*.md` on this branch). No token or credential appears here.

## Ranked problems

### 1. A bad project secret looks like a healthy grant: 9 of 9 boxes blocked for about 18 minutes

- **Hit:** every box, the manager included. **Cost:** about 18 minutes of wall clock with all nine boxes waiting at once, plus 6 to 22 minutes of debugging per box (about 100 box-minutes in total).
- **What happened:** the access requests were granted and `discobox-access list` showed them as healthy, for example `github (GH_TOKEN → github.com, api.github.com) [expires 2026-11-24T18:35:42Z]`. The egress forwarded every call (`blocked: false`), but GitHub rejected the secret behind the stand-in. Each box debugged this on its own (Bearer vs `token` scheme, retries, waiting, `--debug list`) until the manager worked out that the project secret itself was bad. A person updated it at about 16:55. The first 200 came at 16:56, and every first approval then worked without re-approval.
- **Exact errors:**

  ```
  remote: Invalid username or token. Password authentication is not supported for Git operations.
  fatal: Authentication failed for 'https://github.com/tobkorgjz-eng/bw-starter-lab.git/'
  ```
  ```
  {"message": "Bad credentials", "documentation_url": "https://docs.github.com/rest", "status": "401"}
  ```
  ```
  2026-11-24T16:36:17Z  401  GET https://api.github.com/repos/tobkorgjz-eng/bw-starter-lab  (261ms)
  ```
- **Risk:** this pushes boxes to work around the problem. W4 sent a second access request, which broke the one-approval rule, and the manager had to deny it.
- **Ask:** check the secret against its host when it is bound or approved (for GitHub, one `GET /user`). When the upstream answers 401 for a bound secret, say so in `discobox-access list` and in the audit, for example "upstream rejected this secret". Give the person who owns the secret a visible alert.

### 2. Workers cannot reach their manager, so a blocked worker re-requests to get attention

- **Hit:** w1, w3, w4, w5 (stated). **Cost:** one duplicate access request (W4) and some manager time denying it; lost reports.
- **Exact text:** `ListAgents`: `No reachable agents`.
- **What worked the other way:** the manager could reach workers with `discobox send` and `discobox capture --trim`.
- **Risk:** the only channel from a worker back to its manager is a new access request, which is the one thing the rules limit.
- **Ask:** give a box a way to message the box that created it, or show a worker's "blocked" state to its creator.

### 3. A stale `GH_TOKEN` in the tool shell after the secret is fixed

- **Hit:** manager, w3, w6, w8. **Cost:** about 4 minutes for W6. The manager also kept getting 401 after the fix and briefly thought it was still broken.
- **What happened:** the harness shell keeps the environment it started with, and in Claude Code each tool call is a new shell, so an `eval "$(discobox-access env)"` in one call is gone by the next one. The skill documents the `eval`, but not that it must sit in the same command as the push.
- **Exact error (W6, `eval` in an earlier call):** `fatal: could not read Username for 'https://github.com': terminal prompts disabled`
- **Ask:** say plainly in the skill: "run `eval "$(discobox-access env)"` in the same command as the call that needs it". Better still, refresh the variable for new processes on its own when a grant arrives.

### 4. The egress silently refuses a form-encoded POST, and curl prints nothing

- **Hit:** w1 (POST pulls), w7 (POST pulls/1/reviews). **Cost:** a few minutes each, with high risk of confusion. curl printed nothing for W1. For W7 the response body was not JSON, so its client only showed a JSON parse error.
- **Exact audit text** (`curl --data @pr.json` sends `application/x-www-form-urlencoded`):

  ```
  403 BLOCKED  POST https://api.github.com/repos/tobkorgjz-eng/bw-starter-lab/pulls
      reason: route: route POST api.github.com/repos/tobkorgjz-eng/bw-starter-lab/pulls cannot tell what method the body's _method names: it does not parse, or names one twice
  ```
  W7's audit line for the same cause:

  ```
  403 BLOCKED  POST https://api.github.com/repos/tobkorgjz-eng/bw-starter-lab/pulls/1/reviews
      reason: route: route POST api.github.com/repos/tobkorgjz-eng/bw-starter-lab/pulls/*/reviews cannot tell what method the body's _method names: it does not parse, or names one twice
  ```
- **Fix that worked:** `-H "Content-Type: application/json" --data-binary @pr.json`.
- **Ask:** return a JSON error body (with the reason) from the egress, so clients show it, and name the content type in the reason. Mention the `Content-Type` need in the skill's REST example.

### 5. Debugging a write route left a real change that no box could undo, and it then blocked reviews for everyone

- **Hit:** w7 (made it), the manager (blocked by it). **Cost:** small in time, but it left a lasting side effect on a shared repo.
- **What happened:** while working out problem 4, W7 sent a probe `POST .../pulls/3/reviews` with body `{}`. It succeeded (HTTP 200) and created an empty PENDING review (id 6043829619) on PR #3. All boxes act as one GitHub account, so no box can create another review on #3 until that one is submitted or deleted. W7's routes had no submit or delete route, and W7 rightly did not ask for one. It posted its #3 note as an issue comment instead and told the manager. Later the manager's own review on #3 failed:

  ```
  POST pulls/3/reviews -> 422 {"errors":["User can only have one pending review per pull request"]}
  ```
  The manager's note says the draft was "left on #3 by an earlier run". W7's file says its own probe created it (id 6043829619). Both describe the same lock: one draft from one box blocks every box, because they all act as one account. The fallback was an issue comment. At the end of the run the draft was still open, unless a person has deleted it.
- **Risk:** narrow routes still allow real writes. Shared identity means one box's stray write affects every box.
- **Ask:** give each box its own GitHub identity (for example a GitHub App installation per box), so one box's draft cannot block another. Also add a "dry run" or "check route only" mode for `discobox-access`, for example `discobox-access check POST https://...`, that says whether a call would be allowed without sending it. The audit could also list the writes a box made, so a person can clean them up.

### 6. Python `urllib` did not reach the egress, while curl did

- **Hit:** w7. **Cost:** a few minutes; W7 switched to curl for all API calls.
- **What happened:** with the same proxy environment, `urllib` calls left nothing in `discobox-access audit` and the client got a non-JSON error. `curl` worked. W7 did not find the cause.
- **Ask:** check stdlib Python HTTP through the egress (proxy variables and CA bundle), and document what a Python client needs, since many boxes write stdlib-only code.

### 7. The secret name can split: `github-2` vs `github`

- **Hit:** manager. **Cost:** about 10 minutes waiting for a person to approve a second grant, plus a risk of boxes using the wrong secret.
- **What happened:** the manager's first use grant came out under the name `github-2`. The person wanted every box on `github`, so the manager asked again with a separate variable (`BW_GH_TOKEN`) to keep the two apart.
- **Ask:** when a request names a secret that already exists in the project, bind to that one, or warn before creating a second secret with a near-identical name.

### 8. The pre-existing delegation was host-wide, not repo-scoped

- **Hit:** manager. **Cost:** little time, but high risk.
- **What happened:** the `github` delegation covered all of `api.github.com, github.com`. The "this repo only" and "no merge route" limits depended entirely on the manager reading every worker route. The manager wrote a checker script to do it.
- **Ask:** allow (and suggest) a delegation scoped to a repo path, and show in `secret request get` when a worker's route is wider than a given pattern.

### 9. Git does not use the granted token without a helper

- **Hit:** every box that pushed (W7 lists it too). **Cost:** 1 to 2 minutes each, the same discovery made nine times.
- **Exact error:** `fatal: could not read Username for 'https://github.com': No such device or address`
- **Fix that worked:** `git -c credential.helper='!f(){ echo username=x-access-token; echo "password=$GH_TOKEN"; }; f' push ...`
- **Ask:** set up a git credential helper for a GitHub grant by default, or show the one-liner in the skill.

### 10. Machine-readable output mixes progress and results

- **Hit:** manager, w2, w8. **Cost:** a few minutes each.
- `discobox run --from-json` prints progress on stdout before the JSON. Exact error: `jq: parse error: Invalid numeric literal at line 1, column 10` (workaround: `sed -n '/^{/,$p'`).
- `discobox-access wait --json` / `request --json ... "wait": true` writes a progress object and then the result, so a plain `json.load` fails. Exact error: `json.decoder.JSONDecodeError: Extra data: line 2 column 1 (char 404)`. Example progress line: `{"progress":{"status":"pending","kind":"request","requestId":"sreq_g9arc8mgny1ht0sj","waiting":true,...}}`
- **Ask:** the skill says pending notices go to stderr. In practice a box that runs the wait in the background with `2>&1` (W8) or reads the whole output file (W2) gets two JSON objects in one file. A documented rule that "the result is always the last line", or an `--out FILE` that holds only the result, would make this safe to parse.

### 11. `discobox wait` does not treat a pending access request as "blocked"

- **Hit:** manager. **Cost:** a polling loop (Monitor every 60 seconds over `secret request ls`).
- **Ask:** make `discobox wait --until blocked` return when one of the box's access requests is pending.

### 12. A warning on every `discobox run` that reads like a failure

- **Hit:** manager, 8 times. **Cost:** small; it causes doubt.
- **Exact text:** `SSH config not synced: the server refused it (sandbox role permission required for GET /projects/proj_0ew6jzarbv5bs5r7)`
- **Ask:** drop it, or label it clearly as harmless when SSH is not in use.

### 13. Smaller notes

- **Route grammar is long** (w5): finding how to write `issues/*/comments` took a careful read. A short table of common GitHub routes (push, open PR, comment, review) in the skill would help.
- **Rule wording, not Discobox** (w5): the initial commit's committer is `GitHub <noreply@github.com>` (web UI). This is a no-reply identity, but not the one in the box rules. The factory recipe now suggests checking committers too.

### Not Discobox (harness or shell), listed so they are not counted against it

- The zsh glob on `?` in unquoted URLs (w7): `(eval):1: no matches found: https://api.github.com/repos/tobkorgjz-eng/bw-starter-lab/pulls?state=all`
- The working directory moved after a `cd` inside a compound command (w6): `(eval):cd:1: no such file or directory: starter-kit`
- Claude Code blocks a foreground `sleep` (w8, and the manager with `sleep 45`): `Blocked: sleep 70 followed by: cat ... To wait for a condition, use Monitor with an until-loop ...`. Background commands and Monitor worked.
- The boxes' own bugs: a regex in a test (w4), `node -e` argv (w5), a multi-step edit script (w6), a test in W3 that matched the company name "Blade Works" against a "never says works" check, and committed `__pycache__/*.pyc` (w7, w8; both fixed with `git rm --cached` and a `.gitignore`).
- PR heads moved while W7 was reviewing (#7 and #9 were pushed again). W7's script re-reads each head SHA before posting and skips a PR whose notes name an older head. That is a good pattern for any reviewer box.

## What worked well

- **Access requests were fast and narrow.** Every box asked once, with routes for this repo only and no merge route, and got an answer in 1 to 3 minutes. The JSON request form kept routes easy to read. `approve --for 2h` echoed the exact routes and expiry back to the manager.
- **Once the secret was fixed, the first approval kept working.** No box needed a re-approval after the person updated the secret. That is the right behaviour, and it kept the one-approval rule intact.
- **The audit shows the difference between 401 and BLOCKED.** `discobox-access audit` shows an off-route call as `BLOCKED` with a reason, and an on-route call as a plain upstream 401. That is how the manager found the real cause. W3 noted it made the problem "easy to pin down".
- **Credentials are never shown.** `list`, `env`, `--debug list` and the audit never printed a secret, so nine boxes wrote FEEDBACK files with no risk of leaking one.
- **Manager control of workers:** `discobox run --from-json` launched 8 boxes in about 1 minute, and `capture --trim` plus `send`/`send-key` was enough to steer every worker.
- **The box had what the work needed:** `node` was present, so the demo pages' JavaScript could be tested offline, and `unshare -rn` worked, so W7 could run tests with networking fully off. Public `git fetch` and unauthenticated GETs needed no credential.
- **The approvals held through the review and fix round.** Every builder read its review through REST, pushed its fixes and commented with the same single approval. No new access request was needed (W2, W3, W4, W5 and W6 each said so).
- **`discobox-access audit --blocked` gives the exact reason** for a refused call, which W7 called "a one-line fix" once found.
- **A dedicated reviewer box paid for itself.** W7 ran every folder's tests with networking off (`unshare -rn`), re-ran hostile inputs in the re-review, and found three safety gaps that the manager's review had missed. The manager called it "the best decision of the run".
- **Waiting in the background cost nothing:** an access request with `wait`, or a retry loop, ran in the background while the boxes kept coding.

## Time per box (rough minutes)

| Box | Total | Lost to problem 1 | Other problems hit (numbers above) |
| --- | --- | --- | --- |
| manager | 84 | 18 | 5 (422 on #3), 7 (~10 min), 8, 10, 11, 12 |
| w1-client-rules-file | 38 | 19 | 2, 4, 9 |
| w2-client-intake | 50 | 6 (+~20 wait) | 9, 10 |
| w3-upwork-proposal | 60 | 6 (+~18 wait) | 2, 3, 9 |
| w4-booking-bot | 65 | 6 | 2 (duplicate request), 9 |
| w5-faq-bot | 54 | not stated | 2, 9, 13 |
| w6-starter-kit | 73 | 22 | 3 (~4 min), 9 |
| w7-reviewer | 130 | idle wait | 4, 5, 6, 9 |
| w8-scribe | ~70 | 20 | 3, 9, 10 |

Totals include each builder's review fix round (10 to 27 minutes).

"Wait" means idle wall clock while the box waited for the secret fix.

## Sources

One file per box under `FEEDBACK/`, copied byte for byte with `git show origin/<branch>:FEEDBACK/<file> > FEEDBACK/<file>` after the fix round, so merging all branches has no conflict on `FEEDBACK/`:

| File | Branch |
| --- | --- |
| `manager.md` | copied into the scribe box by the manager |
| `w1-client-rules-file.md` | `w1-skill-client-rules-file` |
| `w2-client-intake.md` | `w2-skill-client-intake` |
| `w3-upwork-proposal.md` | `w5-upwork-helper` |
| `w4-booking-bot.md` | `w3-demo-bots-booking` |
| `w5-faq-bot.md` | `w4-demo-bots-faq` |
| `w6-starter-kit.md` | `w2-starter-kit-templates` |
| `w7-reviewer.md` | `w7-reviewer` (re-copied after each W7 push) |
| `w8-scribe.md` | `w8-scribe` |

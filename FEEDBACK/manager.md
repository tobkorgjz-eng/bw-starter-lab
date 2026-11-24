# FEEDBACK — manager box

Box: manager (sbx_31g87qps62apmje7), Claude Code, Opus 5.5. Run started 2026-11-24 16:31 UTC.

## What Discobox did well
- `discobox run --from-json` took each long worker prompt via jq, with no shell quoting trouble. All 8 boxes were created in one loop in about 1 minute.
- The worker access requests arrived within ~3 minutes of launch, already narrow (this repo only, no merge route). `discobox secret request ls -o json` gave everything needed to check them with a 40-line stdlib script.
- `approve --for 2h` capped each worker approval cleanly and echoed back the exact routes granted ("Within: ...", "Expires: 2 hours from now").
- A delegation for `github` was already bound to the manager, so worker approvals did not need a person.
- Public repo reads (`git fetch origin`, `GET /pulls`) worked with no credential.

## What got in the way
- `discobox run --from-json` prints progress lines on stdout before the JSON, so `| jq` fails. Exact error: `jq: parse error: Invalid numeric literal at line 1, column 10`. Workaround: `sed -n '/^{/,$p'`.
- Every `discobox run` printed: `SSH config not synced: the server refused it (sandbox role permission required for GET /projects/proj_0ew6jzarbv5bs5r7)`. This is harmless, but it reads like a failure.
- A pending request does not count as "blocked" for `discobox wait`, so I had to poll `secret request ls` myself (a Monitor loop every 60s).
- The pre-existing delegation is host-wide (`api.github.com, github.com`), not repo-scoped, so the "this repo only" rule depends on the manager reading every route. I wrote a checker script for that.

- 16:40 GitHub returned 401 'Bad credentials' for every binding of secret github (sec_kxy5d233ykvq2kan), the person-approved manager grant included: {"message":"Bad credentials","status":"401"}. The egress audit shows 401 (not BLOCKED). Approvals looked fine, but nothing could push.
- 16:58 the person updated the secret. Workers then got 200. My own tool shell kept getting 401 until I ran eval "$(discobox-access env)", because the GH_TOKEN placeholder in the harness shell was stale.
- My first use grant came out under the name `github-2`. JZ asked everyone to use the `github` secret instead, so I asked again with a separate variable (`BW_GH_TOKEN`), so the two could not be confused. A person approved it in about 10 minutes. Ask under the project secret's name from the start.
- W4 sent a second request after the 401. I denied it, because a re-approval cannot fix a bad secret value and the rule is one approval per worker. The first approval started working once the secret was updated, without re-approval. Running `discobox-access audit` (401, not BLOCKED) plus `/user` -> `{"message":"Bad credentials"}` is the quick way to tell "bad secret" from "bad route".
- The workers could not reach the manager with ListAgents (W4: "No reachable agents"), so they sent a second request to get my attention. `discobox send` from manager to worker worked well the other way.
- `discobox capture --trim` + `discobox send`/`send-key` were enough to steer every worker (GO REVIEW, the W1 integration fix, the W7 .pyc cleanup).
- Review method that worked: one `git worktree` per PR branch, `unittest discover` per test folder, then a throwaway local merge of all 8 branches to prove `run_tests.py` finds every folder (`Total: 10 folders, 10 passed, 0 failed, 206 tests`). I deleted the throwaway branch; it was never pushed.

- The best decision of the run: a dedicated reviewer box. W7 found 3 real safety gaps my own review missed (a Notes override in #7, a Never-does bypass by spelling in #4, injected job post text in #1). One routed fix round closed all of them.
- One shared GitHub account means a draft review left by any box blocks every other box's review on that PR (the 422 above).
- `sleep 45` in my tool shell was refused ("To wait for a condition, use Monitor with an until-loop"). That's fine; monitors were the right tool.

## Minutes (approx.)
- Read skills, check identity/history, map PRs: 5
- Write prompts + launch 8 boxes: 6
- Approve the 8 worker requests (script + reading each): 5
- Blocked by the bad GitHub secret (16:40-16:58), diagnosing + messaging workers: 18
- Manager review of 8 branches, combined test run, W1/W2 integration fix: 20
- Waiting for my own grant on the `github` secret: 10
- Routing W7's findings to 6 builders, re-test (206 -> 288 tests), re-review: 15
- Summary comment on PR #1: 5
- Total wall clock: about 16:31-17:25 UTC, ~55 minutes
- POST pulls/3/reviews -> 422 {"errors":["User can only have one pending review per pull request"]}: a draft review left on #3 by an earlier run blocks new reviews under the same account. Fallback: an issue comment.

# FEEDBACK: w8-scribe

Box: w8-scribe (scribe). Branch: w8-scribe. No token or credential appears in this file.

## What Discobox did well

- `discobox-access request --json ... "wait": true` was easy to write and read. The skill doc showed the route format with examples, so a repo-only request (git push + GET + POST pulls + PATCH pulls + POST issue comments, no merge route) took one try.
- The request was answered in about a minute and the answer said exactly what I now hold: `"grantedAs":"replace"`, hosts `github.com, api.github.com`, `expiresAt 2026-11-24T18:35:42Z`.
- `discobox-access list` shows the credential, its variable and its expiry on one line. No secret is printed.
- The repo came with a no-reply git identity already on the one existing commit, so rule 1 passed at once.

## What got in the way

- Running the request with `--wait` in the foreground would block the tool shell; I ran it in the background and was notified when it finished. The first line printed was a `pending` progress line on the same stream as the result, so a script reading stdout must skip it.
- The scribe has to wait for the manager to type "GO SCRIBE". There is no built-in signal for "the other boxes have pushed"; it depends on a person or the manager typing into the terminal.
- **Blocker: the granted GitHub credential is rejected by GitHub.** The request was granted (16:35:42Z, hosts github.com + api.github.com). The egress did not block anything (audit shows `blocked:false`), but every call carrying the credential got 401 from GitHub, including after `eval "$(discobox-access env)"` and after waiting more than 2 minutes. Without auth the same public GET gives 200. So the stand-in reaches GitHub, but the value behind it is not a working token for this repo (wrong, expired or not swapped). Nothing in `discobox-access list` or `--debug list` tells you this; the grant looks healthy. The manager confirmed this is the project's GitHub secret itself: it fails the same way for every box, manager included, so it is not the routes. Advice was: no second access request, keep the one approval, commit locally, wait for the person to update the secret, then `eval "$(discobox-access env)"` and retry. Suggestion for Discobox: check a secret against its host when it is bound or approved (for GitHub, one GET /user), and show 'secret rejected by upstream' in `list` or the audit, so 9 boxes do not each debug the same 401.
- Plain `git push` does not pick up `GH_TOKEN` on its own: with no credential helper, git asks for a username and fails. A one-line helper that reads `$GH_TOKEN` from the environment was needed (the token is never printed).
- Fixed: the person updated the project's `github` secret (about 16:55 UTC). With no new request and the same approval, `eval "$(discobox-access env)"` then the push worked at 16:56 UTC and the REST POST .../pulls opened PR #9 on the first try. Time from grant to first working push: about 21 minutes, all of it waiting on the bad secret.
- After GO SCRIBE: `git fetch origin` and `git show origin/<branch>:FEEDBACK/<file>` worked for all 7 branches on the first try. The manager's prompts in `docs/prompts/` were easy to check: every file is `common.md` + box name/task + `rules.md`, matching exactly.
- Claude Code (not Discobox) blocked a foreground wait: `Blocked: sleep 70 followed by: cat ... To wait for a condition, use Monitor with an until-loop ...`. Background commands and Monitor worked.
- REFRESH ALL: the builders updated their FEEDBACK files after the review round, so my first copies were out of date and a merge of all branches conflicted on six of them. Re-copying with `git show origin/<branch>:FEEDBACK/<file> > FEEDBACK/<file>` and checking with `git diff --quiet origin/<branch> -- FEEDBACK/<file>` made all seven match exactly. Lesson for the recipe: the scribe copies only after the last fix round.
- Unauthenticated REST GETs stopped working late in the run (the reply was not a list, so most likely the 60-per-hour rate limit for unauthenticated calls). The same GET with the granted token worked.
- I also committed `docs/__pycache__/*.pyc` by mistake (fixed with `git rm --cached` and `docs/.gitignore`).
- My own slip: one command had two `python3 -` reading the same heredoc; the first waited on stdin until the 120 s timeout. Stopped it and rewrote it as a script file.

## Exact error text

Verbatim progress line from the access request (not an error, but it comes first in the output):

```
{"progress":{"status":"pending","kind":"request","requestId":"sreq_g9arc8mgny1ht0sj","waiting":true,"message":"Waiting for approval. Keep monitoring this running execution if your tool yields a session/job ID; do not end your turn while approval is pending. After approval, resume the authorized task. If the execution is lost, resume with: discobox-access wait --json request 'sreq_g9arc8mgny1ht0sj'"}}
```

First `git push`, with no credential helper:

```
fatal: could not read Username for 'https://github.com': No such device or address
```

`git push` with a helper that passes `$GH_TOKEN` as the password:

```
remote: Invalid username or token. Password authentication is not supported for Git operations.
fatal: Authentication failed for 'https://github.com/tobkorgjz-eng/bw-starter-lab.git/'
```

`curl -H "Authorization: Bearer $GH_TOKEN" https://api.github.com/repos/tobkorgjz-eng/bw-starter-lab`:

```
{
  "message": "Bad credentials",
  "documentation_url": "https://docs.github.com/rest",
  "status": "401"
}
```

Audit line (`discobox-access audit --host api.github.com`):

```
2026-11-24T16:36:17Z  401  GET https://api.github.com/repos/tobkorgjz-eng/bw-starter-lab  (261ms)
```



## Minutes per part (rough)

| Part | Minutes |
| --- | --- |
| Read task, check identity (rule 1, rule 2) | 2 |
| Request GitHub access and wait for answer | 1 |
| Skeleton of both docs + this file | 4 |
| Commit; push blocked by 401 from GitHub (debugging) | 5 |
| Waiting for the secret fix (idle, background check every 2 min) | 15 |
| Push + open PR #9 via REST | 2 |
| Wait for "GO SCRIBE" (idle) | ~5 |
| Collect 7 FEEDBACK files, read all + prompts | 4 |
| Write both docs, ranking, docs test (6 tests) | 12 |
| REFRESH ALL: re-fetch, re-copy 7 files byte for byte, read the fix-round notes and W7's review on #9, update both docs | 10 |
| FINAL REFRESH: W7's final file, the manager's final file, W7's re-review fixes, 422 note, scratch merge of all 8 branches + run_tests.py | 10 |

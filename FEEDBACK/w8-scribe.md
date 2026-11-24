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
- **Blocker: the granted GitHub credential is rejected by GitHub.** The request was granted (16:35:42Z, hosts github.com + api.github.com). The egress did not block anything (audit shows `blocked:false`), but every call carrying the credential got 401 from GitHub, including after `eval "$(discobox-access env)"` and after waiting more than 2 minutes. Without auth the same public GET gives 200. So the stand-in reaches GitHub, but the value behind it is not a working token for this repo (wrong, expired or not swapped). Nothing in `discobox-access list` or `--debug list` tells you this; the grant looks healthy.
- Plain `git push` does not pick up `GH_TOKEN` on its own: with no credential helper, git asks for a username and fails. A one-line helper that reads `$GH_TOKEN` from the environment was needed (the token is never printed).
- (to update after GO SCRIBE if anything else goes wrong)

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

(to update after GO SCRIBE)

## Minutes per part (rough)

| Part | Minutes |
| --- | --- |
| Read task, check identity (rule 1, rule 2) | 2 |
| Request GitHub access and wait for answer | 1 |
| Skeleton of both docs + this file | 4 |
| Commit; push blocked by 401 from GitHub (debugging) | 5 so far |
| Wait for "GO SCRIBE" | (to fill) |
| Collect FEEDBACK files, write both docs | (to fill) |

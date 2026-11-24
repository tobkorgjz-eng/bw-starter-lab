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
- (to update after GO SCRIBE if anything else goes wrong)

## Exact error text

Verbatim progress line from the access request (not an error, but it comes first in the output):

```
{"progress":{"status":"pending","kind":"request","requestId":"sreq_g9arc8mgny1ht0sj","waiting":true,"message":"Waiting for approval. Keep monitoring this running execution if your tool yields a session/job ID; do not end your turn while approval is pending. After approval, resume the authorized task. If the execution is lost, resume with: discobox-access wait --json request 'sreq_g9arc8mgny1ht0sj'"}}
```

(to update after GO SCRIBE)

## Minutes per part (rough)

| Part | Minutes |
| --- | --- |
| Read task, check identity (rule 1, rule 2) | 2 |
| Request GitHub access and wait for answer | 1 |
| Skeleton of both docs + this file | 4 |
| Commit, push, open PR via REST | (to fill) |
| Wait for "GO SCRIBE" | (to fill) |
| Collect FEEDBACK files, write both docs | (to fill) |

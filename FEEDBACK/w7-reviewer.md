# FEEDBACK — w7-reviewer

Draft; updated at the end of the review.

## What Discobox did well
- One scoped access request (this repo only, push + open PR + reviews/comments,
  no merge route) was answered within minutes; `discobox-access list` and the
  JSON request form kept the routes easy to read and narrow.
- `unshare -rn` worked in the box, so each folder's tests could be run with
  networking fully disabled, which shows they really pass offline.
- The repo is public, so `git fetch origin` and unauthenticated GETs worked for
  preparation before any credential was needed.

## What got in the way
- After approval, authenticated GitHub API calls failed. Exact response to
  `GET https://api.github.com/repos/tobkorgjz-eng/bw-starter-lab` with the
  granted variable (HTTP 401):

  ```
  {
    "message": "Bad credentials",
    "documentation_url": "https://docs.github.com/rest",
    "status": "401"
  }
  ```
  Per the manager, this is the project's GitHub secret itself, not the routes.
  Work was committed locally while waiting for the secret to be updated.
- zsh treats `?` in an unquoted URL as a glob: `(eval):1: no matches found:
  https://api.github.com/repos/tobkorgjz-eng/bw-starter-lab/pulls?state=all`.
  Quoting the URL fixed it.

## Rough time
- Identity check, git config, access request: ~5 min (plus waiting for approval)
- Scan script + tests: ~15 min
- Preliminary read/test of PRs #1–#5: ~20 min

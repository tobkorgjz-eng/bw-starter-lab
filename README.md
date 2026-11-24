# bw-starter-lab
Practice lab: client bot starter kit, demo bots, Upwork helper (generic, made-up data)

- `starter-kit/` – the client pack: rules, prompt templates, folder layout and
  a plain-English client guide. See `starter-kit/README.md`.

## Running the tests

```sh
python3 run_tests.py
```

`run_tests.py` finds every `test_*.py` in the repo (skipping `.git`), runs each
folder's tests with `unittest` in its own subprocess, prints a PASS/FAIL line
per folder and a total, and exits non-zero if anything fails. Standard library
only, no network calls. Its own tests are in `test_run_tests.py`.

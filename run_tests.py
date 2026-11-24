#!/usr/bin/env python3
"""Run every test in this repository.

Usage:
    python3 run_tests.py            # run all tests under the repo root
    python3 run_tests.py --root DIR # run all tests under DIR instead

How it works:
- Finds every file named test_*.py under the root, skipping .git and
  __pycache__ folders.
- Groups the files by the folder they are in. Each folder runs in its own
  Python subprocess with unittest, so two folders can both have a module
  called (for example) test_bot.py without clashing.
- If a test folder is a package (it has __init__.py), the subprocess starts
  from the folder above the top package and imports the tests by their
  dotted name (for example tests.test_templates), the same way
  `python3 -m unittest discover -s <folder> -t <folder>` would.
- Prints one PASS/FAIL line per folder and a total. Output from a failing
  folder is printed in full so you can see what went wrong.

Exit code: 0 if every folder passed, 1 if any folder failed or no tests
were found. Standard library only; this script makes no network calls.
"""

import argparse
import os
import re
import subprocess
import sys

SKIP_DIRS = {".git", "__pycache__"}
TEST_FILE = re.compile(r"^test_.*\.py$")
IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
RAN_LINE = re.compile(r"^Ran (\d+) tests?\b", re.M)
TIMEOUT_SECONDS = 600


def find_test_files(root):
    """Return {folder: [test file names]} for every test_*.py under root."""
    found = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        tests = sorted(f for f in filenames if TEST_FILE.match(f))
        if tests:
            found[dirpath] = tests
    return found


def import_root(folder, root):
    """Return (start_dir, dotted_prefix) for importing tests in folder.

    Walks up while the folder is a package (has __init__.py), but never
    above root.
    """
    root = os.path.abspath(root)
    folder = os.path.abspath(folder)
    parts = []
    current = folder
    while (current != root
           and os.path.isfile(os.path.join(current, "__init__.py"))):
        parts.insert(0, os.path.basename(current))
        current = os.path.dirname(current)
    return current, ".".join(parts)


def module_names(folder, files, root):
    """Return (start_dir, [dotted module names], [bad file names])."""
    start, prefix = import_root(folder, root)
    names, bad = [], []
    for name in files:
        stem = name[:-3]
        package_parts = prefix.split(".") if prefix else []
        if not all(IDENTIFIER.match(p) for p in package_parts + [stem]):
            bad.append(name)
            continue
        names.append(".".join(package_parts + [stem]))
    return start, names, bad


def run_folder(folder, files, root):
    """Run one folder's tests in a subprocess. Return a result dict."""
    start, names, bad = module_names(folder, files, root)
    result = {"folder": folder, "passed": False, "tests": 0, "output": ""}
    if bad:
        result["output"] = ("These file names cannot be imported as Python "
                            "modules: " + ", ".join(bad) + "\n")
        return result
    cmd = [sys.executable, "-m", "unittest"] + names
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    try:
        proc = subprocess.run(cmd, cwd=start, env=env, capture_output=True,
                              text=True, timeout=TIMEOUT_SECONDS,
                              stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        result["output"] = "Timed out after %d seconds\n" % TIMEOUT_SECONDS
        return result
    output = proc.stdout + proc.stderr
    ran = RAN_LINE.findall(output)
    result["tests"] = int(ran[-1]) if ran else 0
    result["output"] = output
    result["passed"] = proc.returncode == 0 and result["tests"] > 0
    if proc.returncode == 0 and result["tests"] == 0:
        result["output"] += "\nNo tests ran in this folder.\n"
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run every test_*.py "
                                     "in the repo, one folder at a time.")
    parser.add_argument("--root", default=os.path.dirname(
        os.path.abspath(__file__)), help="folder to search (default: repo root)")
    args = parser.parse_args(argv)
    root = os.path.abspath(args.root)

    groups = find_test_files(root)
    if not groups:
        print("No test_*.py files found under %s" % root)
        return 1

    results = []
    for folder in sorted(groups):
        res = run_folder(folder, groups[folder], root)
        results.append(res)
        label = os.path.relpath(folder, root)
        status = "PASS" if res["passed"] else "FAIL"
        print("%s  %s  (%d tests)" % (status, label, res["tests"]), flush=True)
        if not res["passed"]:
            for line in res["output"].rstrip().splitlines():
                print("      " + line)

    failed = [r for r in results if not r["passed"]]
    total_tests = sum(r["tests"] for r in results)
    print("Total: %d folders, %d passed, %d failed, %d tests"
          % (len(results), len(results) - len(failed), len(failed), total_tests))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

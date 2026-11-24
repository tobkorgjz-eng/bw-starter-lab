"""Tests for run_tests.py. Standard library only; no network.

Every test builds a small made-up repo in a temporary folder and runs
run_tests.py against it with --root, so these tests never run themselves.
"""

import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
RUNNER = os.path.join(HERE, "run_tests.py")
sys.path.insert(0, HERE)
import run_tests  # noqa: E402

PASSING = """import unittest

class T(unittest.TestCase):
    def test_ok(self):
        self.assertEqual(1 + 1, 2)
"""

FAILING = """import unittest

class T(unittest.TestCase):
    def test_bad(self):
        self.assertEqual(1 + 1, 3)
"""

# Records which folder it was imported from, so a clash would show up.
WHERE = """import os, unittest

class T(unittest.TestCase):
    def test_folder(self):
        here = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
        self.assertEqual(here, {expected!r})
"""


def write(root, rel, text=""):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


class RunnerTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()

    def run_runner(self):
        proc = subprocess.run([sys.executable, RUNNER, "--root", self.root],
                              capture_output=True, text=True, timeout=120,
                              stdin=subprocess.DEVNULL)
        return proc.returncode, proc.stdout

    def test_all_pass(self):
        write(self.root, "alpha/test_a.py", PASSING)
        write(self.root, "beta/deep/test_b.py", PASSING)
        code, out = self.run_runner()
        self.assertEqual(code, 0, out)
        self.assertIn("PASS  alpha  (1 tests)", out)
        self.assertIn(os.path.join("beta", "deep"), out)
        self.assertIn("Total: 2 folders, 2 passed, 0 failed, 2 tests", out)

    def test_failure_gives_non_zero_exit(self):
        write(self.root, "good/test_good.py", PASSING)
        write(self.root, "bad/test_bad.py", FAILING)
        code, out = self.run_runner()
        self.assertEqual(code, 1)
        self.assertIn("FAIL  bad", out)
        self.assertIn("PASS  good", out)
        self.assertIn("1 passed, 1 failed", out)
        self.assertIn("AssertionError", out)  # failing output is shown

    def test_same_module_name_in_two_folders(self):
        write(self.root, "one/test_bot.py", WHERE.format(expected="one"))
        write(self.root, "two/test_bot.py", WHERE.format(expected="two"))
        code, out = self.run_runner()
        self.assertEqual(code, 0, out)
        self.assertIn("2 passed, 0 failed", out)

    def test_package_tests_folder(self):
        write(self.root, "tool/helper.py", "VALUE = 7\n")
        write(self.root, "tool/tests/__init__.py")
        write(self.root, "tool/tests/test_helper.py",
              "import os, sys, unittest\n"
              "sys.path.insert(0, os.path.dirname(os.path.dirname("
              "os.path.abspath(__file__))))\n"
              "import helper\n"
              "class T(unittest.TestCase):\n"
              "    def test_value(self):\n"
              "        self.assertEqual(helper.VALUE, 7)\n"
              "        self.assertEqual(__name__, 'tests.test_helper')\n")
        code, out = self.run_runner()
        self.assertEqual(code, 0, out)
        self.assertIn("PASS  " + os.path.join("tool", "tests"), out)

    def test_skips_git_and_pycache(self):
        write(self.root, "ok/test_ok.py", PASSING)
        write(self.root, ".git/hooks/test_hidden.py", FAILING)
        write(self.root, "ok/__pycache__/test_cached.py", FAILING)
        code, out = self.run_runner()
        self.assertEqual(code, 0, out)
        self.assertIn("Total: 1 folders", out)

    def test_no_tests_found_fails(self):
        write(self.root, "docs/README.md", "# nothing here\n")
        code, out = self.run_runner()
        self.assertEqual(code, 1)
        self.assertIn("No test_*.py files found", out)

    def test_file_with_no_test_cases_fails(self):
        write(self.root, "empty/test_empty.py", "X = 1\n")
        code, out = self.run_runner()
        self.assertEqual(code, 1)
        self.assertIn("FAIL  empty  (0 tests)", out)

    def test_bad_module_name_fails(self):
        write(self.root, "odd/test_odd-name.py", PASSING)
        code, out = self.run_runner()
        self.assertEqual(code, 1)
        self.assertIn("cannot be imported", out)


class FindTestsInThisRepoTest(unittest.TestCase):
    def test_finds_starter_kit_tests(self):
        groups = run_tests.find_test_files(HERE)
        rel = {os.path.relpath(d, HERE) for d in groups}
        self.assertIn(os.path.join("starter-kit", "rules"), rel)
        self.assertIn(os.path.join("starter-kit", "templates", "tests"), rel)
        self.assertIn(".", rel)  # this file
        self.assertFalse(any(p.split(os.sep)[0] == ".git" for p in rel))


if __name__ == "__main__":
    unittest.main()

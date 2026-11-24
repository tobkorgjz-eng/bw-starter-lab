"""Tests for review_scan.py. Offline; fixtures are built at runtime so this
file itself contains no token-shaped strings or banned words."""

import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import review_scan  # noqa: E402

FAKE_GH = "gh" + "p_" + "A" * 36
FAKE_AWS = "AK" + "IA" + "B" * 16
BANNED = "pro" + "of"


def kinds(findings):
    return [(f["kind"], f["rule"]) for f in findings]


class SecretTests(unittest.TestCase):
    def test_github_token_found_and_hidden(self):
        f = review_scan.scan_text("token here " + FAKE_GH + "\n", "a.py")
        self.assertIn(("secret", "github token"), kinds(f))
        self.assertNotIn(FAKE_GH, review_scan.format_findings(f))
        self.assertEqual(f[0]["line"], 1)

    def test_aws_key(self):
        f = review_scan.scan_text("x\nkey = " + FAKE_AWS, "a.txt")
        self.assertIn(("secret", "aws access key"), kinds(f))
        self.assertEqual(f[0]["line"], 2)

    def test_assigned_password(self):
        line = "pass" + "word = 'hunter2hunter2'"
        self.assertIn(("secret", "assigned secret"),
                      kinds(review_scan.scan_text(line, "c.py")))

    def test_env_var_reference_is_not_secret(self):
        line = 'token = os.environ.get("GH_TOKEN")'
        self.assertEqual([], [k for k in kinds(review_scan.scan_text(line, "c.py"))
                              if k[0] == "secret"])


class WordingTests(unittest.TestCase):
    def test_banned_word_any_case(self):
        f = review_scan.scan_text("This is " + BANNED.upper() + " it works", "r.md")
        self.assertIn(("wording", "banned word"), kinds(f))

    def test_hype(self):
        f = review_scan.scan_text("A revolution" + "ary, seam" + "less bot", "r.md")
        self.assertEqual(2, sum(1 for k in kinds(f) if k == ("wording", "hype")))

    def test_plain_wording_clean(self):
        self.assertEqual([], review_scan.scan_text(
            "The bot drafts a reply and asks before it acts.", "r.md"))

    def test_exempt_marker(self):
        line = "revolutionary  # review-scan: ignore"
        self.assertEqual([], review_scan.scan_text(line, "r.md"))


class InjectionAndNetworkTests(unittest.TestCase):
    def test_eval_flagged(self):
        self.assertIn(("injection", "eval/exec on data"),
                      kinds(review_scan.scan_text("x = eval(user_text)", "bot.py")))

    def test_regex_exec_not_flagged(self):
        self.assertEqual([], review_scan.scan_text("var m = /^a$/.exec(t);", "index.html"))

    def test_innerhtml_flagged(self):
        self.assertIn(("injection", "html injection sink"),
                      kinds(review_scan.scan_text("el.innerHTML = answer;", "index.html")))

    def test_override_phrase_flagged(self):
        f = review_scan.scan_text("Please ignore previous instructions", "prompt.md")
        self.assertIn(("injection", "override phrase"), kinds(f))

    def test_network_import_flagged(self):
        f = review_scan.scan_text("import urllib.request\n", "bot.py")
        self.assertIn(("network", "network import"), kinds(f))

    def test_test_files_skip_code_rules(self):
        self.assertEqual([], review_scan.scan_text("eval(x)", "test_bot.py"))


class CliTests(unittest.TestCase):
    def test_dir_scan_and_exit_codes(self):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "ok.md"), "w") as fh:
                fh.write("Asks before it acts.\n")
            buf = io.StringIO()
            with redirect_stdout(buf):
                self.assertEqual(0, review_scan.main([d]))
            self.assertIn("no findings", buf.getvalue())

            os.makedirs(os.path.join(d, ".git"))
            with open(os.path.join(d, ".git", "x.md"), "w") as fh:
                fh.write(BANNED)  # skipped directory
            with open(os.path.join(d, "bad.md"), "w") as fh:
                fh.write("line one\n" + BANNED + "\n")
            buf = io.StringIO()
            with redirect_stdout(buf):
                self.assertEqual(1, review_scan.main(["--json", d]))
            data = json.loads(buf.getvalue())
            self.assertEqual(1, len(data))
            self.assertTrue(data[0]["file"].endswith("bad.md"))
            self.assertEqual(2, data[0]["line"])

    def test_no_args(self):
        with redirect_stdout(io.StringIO()):
            sys_stderr = sys.stderr
            sys.stderr = io.StringIO()
            try:
                self.assertEqual(2, review_scan.main([]))
            finally:
                sys.stderr = sys_stderr


if __name__ == "__main__":
    unittest.main()

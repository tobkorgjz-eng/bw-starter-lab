import ast
import io
import socket
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import proposal as pr  # noqa: E402

SAMPLES = HERE / "samples"
EXPERIENCE = "2 years building AI assistant teams"
# (file, expected score, reason fragments that must appear)
CASES = [
    ("job_clinic_assistant.txt", 5,
     ["skills we offer appear", "strong overlap", "budget stated: $1,200 fixed",
      "clear description"]),
    ("job_inventory_report.txt", 3,
     ["budget stated: $35/hr", "short description",
      "required skills we do not offer: power bi, sql server"]),
    ("job_crypto_bot.txt", 1,
     ["none of our skills", "no budget stated", "red flags", "unpaid test",
      "telegram"]),
]


def load(name):
    return pr.parse_job_post((SAMPLES / name).read_text(encoding="utf-8"))


class ScoreTests(unittest.TestCase):
    def test_scores(self):
        for name, expected, _ in CASES:
            with self.subTest(name):
                score, _, _, _ = pr.score_fit(load(name))
                self.assertEqual(score, expected)

    def test_reasons(self):
        for name, _, fragments in CASES:
            with self.subTest(name):
                reasons = " | ".join(pr.score_fit(load(name))[1])
                for frag in fragments:
                    self.assertIn(frag, reasons)

    def test_score_always_in_range(self):
        for text in ["", "Title: x", "Description: telegram unpaid test whatsapp"]:
            score = pr.score_fit(pr.parse_job_post(text))[0]
            self.assertTrue(1 <= score <= 5)

    def test_trading_bot_is_not_a_chatbot(self):
        _, _, matched, _ = pr.score_fit(load("job_crypto_bot.txt"))
        self.assertNotIn("chatbot", matched)


class DraftRuleTests(unittest.TestCase):
    def drafts(self):
        return [(n, pr.report(load(n))) for n, _, _ in CASES]

    def test_experience_line_once(self):
        for name, out in self.drafts():
            with self.subTest(name):
                self.assertEqual(out.count(EXPERIENCE), 1)

    def test_never_proof(self):
        # inventory post says "proof of concept"; it must not be echoed
        self.assertIn("proof", (SAMPLES / "job_inventory_report.txt").read_text().lower())
        for name, out in self.drafts():
            with self.subTest(name):
                self.assertNotIn("proof", out.lower())

    def test_no_hype_words(self):
        # inventory title says "Best expert"; crypto says "guarantees".
        # The reasons may quote a red flag; the draft itself must be clean.
        for name, _, _ in CASES:
            with self.subTest(name):
                self.assertEqual(pr.find_banned(pr.draft_proposal(load(name))), [])

    def test_honest_about_missing_skills(self):
        out = pr.draft_proposal(load("job_inventory_report.txt"))
        self.assertIn("we have not worked with power bi, sql server", out)

    def test_only_claims_our_skills(self):
        for name, _, _ in CASES:
            _, _, matched, _ = pr.score_fit(load(name))
            self.assertTrue(set(matched) <= set(pr.OUR_SKILLS))

    def test_short(self):
        for name, _, _ in CASES:
            words = len(pr.draft_proposal(load(name)).split())
            self.assertLessEqual(words, pr.MAX_DRAFT_WORDS)

    def test_low_score_warns(self):
        self.assertIn("consider not applying", pr.draft_proposal(load("job_crypto_bot.txt")))
        self.assertNotIn("consider not applying", pr.draft_proposal(load("job_clinic_assistant.txt")))

    def test_guard_raises_on_banned_name(self):
        with self.assertRaises(ValueError):
            pr.draft_proposal(load("job_clinic_assistant.txt"), freelancer="Best Team")


class NothingSentTests(unittest.TestCase):
    NETWORK_MODULES = {"socket", "urllib", "http", "smtplib", "ftplib",
                       "requests", "ssl", "email", "subprocess", "asyncio"}

    def test_no_network_imports(self):
        tree = ast.parse((HERE / "proposal.py").read_text(encoding="utf-8"))
        names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names |= {a.name.split(".")[0] for a in node.names}
            elif isinstance(node, ast.ImportFrom):
                names.add((node.module or "").split(".")[0])
        self.assertEqual(names & self.NETWORK_MODULES, set())

    def test_cli_opens_no_socket_and_says_not_sent(self):
        def refuse(*a, **k):
            raise AssertionError("network use attempted")
        with mock.patch.object(socket, "socket", refuse), \
                mock.patch.object(socket, "create_connection", refuse):
            for name, _, _ in CASES:
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = pr.main([str(SAMPLES / name)])
                self.assertEqual(rc, 0)
                self.assertIn("not sent", buf.getvalue())

    def test_out_file_is_only_side_effect(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "draft.txt"
            pr.main([str(SAMPLES / "job_clinic_assistant.txt"), "--out", str(out)])
            self.assertEqual([p.name for p in Path(d).iterdir()], ["draft.txt"])
            self.assertIn("FIT SCORE: 5/5", out.read_text(encoding="utf-8"))


class SkillFileTests(unittest.TestCase):
    def test_frontmatter(self):
        text = (HERE / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"))
        head = text.split("---\n")[1]
        self.assertIn("name: upwork-proposal\n", head)
        self.assertIn("description: ", head)
        self.assertIn(EXPERIENCE, text)
        self.assertIn("Never send anything", text)


if __name__ == "__main__":
    unittest.main()

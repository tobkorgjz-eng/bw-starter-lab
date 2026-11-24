import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import proposal_helper as ph  # noqa: E402

SAMPLES = HERE.parent / "samples"


def load(name):
    return ph.parse_job_post((SAMPLES / name).read_text(encoding="utf-8"))


class ParseTests(unittest.TestCase):
    def test_parse_fields(self):
        job = load("job_data_cleanup.txt")
        self.assertEqual(job["title"], "Clean up and merge monthly sales CSV files")
        self.assertEqual(job["budget"], "$300 fixed")
        self.assertIn("csv", job["skills"])
        self.assertTrue(job["description"].startswith("We are a small"))

    def test_defaults_when_missing(self):
        job = ph.parse_job_post("Just some text with no headers.")
        self.assertEqual(job["title"], "Untitled job")
        self.assertEqual(job["client"], "there")
        self.assertEqual(job["budget"], "")


class ChecklistTests(unittest.TestCase):
    def test_good_fit(self):
        checks, score, matched = ph.fit_checklist(load("job_data_cleanup.txt"))
        self.assertEqual(score, 100)
        self.assertIn("python", matched)

    def test_poor_fit_flags(self):
        checks, score, _ = ph.fit_checklist(load("job_quick_bot.txt"))
        results = {name: ok for name, ok, _ in checks}
        self.assertFalse(results["No red flags"])
        self.assertFalse(results["Budget stated"])
        self.assertLess(score, 50)


class DraftTests(unittest.TestCase):
    def test_draft_contains_parts(self):
        out = ph.draft_proposal(load("job_data_cleanup.txt"), freelancer="Test Person")
        self.assertIn("FIT CHECKLIST", out)
        self.assertIn("Hi Maple Lantern Bakery", out)
        self.assertIn("$300 fixed", out)
        self.assertIn("Test Person", out)
        self.assertNotIn("$client", out)

    def test_custom_template(self):
        job = load("job_quick_bot.txt")
        out = ph.draft_proposal(job, template="Re: $title / $unknown")
        self.assertIn("Re: Need chatbot built urgent asap / $unknown", out)

    def test_cli_writes_file(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "draft.txt"
            rc = ph.main([str(SAMPLES / "job_data_cleanup.txt"), "--out", str(out)])
            self.assertEqual(rc, 0)
            self.assertIn("DRAFT PROPOSAL", out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

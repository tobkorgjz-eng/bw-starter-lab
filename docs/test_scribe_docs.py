"""Offline checks for the scribe docs (w8-scribe).

Run from the repo root:
    python3 -m unittest discover -s docs -t docs
"""
import os
import re
import unittest

DOCS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(DOCS)
SCRIBE_DOCS = ["factory-recipe.md", "discobox-feedback.md"]
FEEDBACK_FILES = [
    "manager.md", "w1-client-rules-file.md", "w2-client-intake.md",
    "w3-upwork-proposal.md", "w4-booking-bot.md", "w5-faq-bot.md",
    "w6-starter-kit.md", "w7-reviewer.md", "w8-scribe.md",
]
# Common token shapes (GitHub, Anthropic, generic bearer values).
TOKEN_RE = re.compile(
    r"(ghp_|gho_|ghs_|ghu_|github_pat_|sk-ant-)[A-Za-z0-9_]{10,}"
    r"|Bearer\s+[A-Za-z0-9_\-\.]{30,}"
)
BANNED_WORD = "pro" + "of"  # built from parts so this file stays clean


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


class ScribeDocsTest(unittest.TestCase):
    def test_docs_exist_and_are_filled(self):
        for name in SCRIBE_DOCS:
            text = read(os.path.join(DOCS, name))
            self.assertNotIn("SKELETON", text, name)
            self.assertNotIn("_to fill_", text, name)

    def test_banned_word_absent_from_scribe_docs(self):
        for name in SCRIBE_DOCS:
            text = read(os.path.join(DOCS, name)).lower()
            self.assertNotIn(BANNED_WORD, text, name)

    def test_no_token_like_strings(self):
        paths = [os.path.join(DOCS, n) for n in SCRIBE_DOCS]
        paths += [os.path.join(ROOT, "FEEDBACK", n) for n in FEEDBACK_FILES]
        for path in paths:
            self.assertIsNone(TOKEN_RE.search(read(path)), path)

    def test_every_feedback_file_present_and_listed(self):
        feedback_doc = read(os.path.join(DOCS, "discobox-feedback.md"))
        for name in FEEDBACK_FILES:
            self.assertTrue(
                os.path.isfile(os.path.join(ROOT, "FEEDBACK", name)), name)
            self.assertIn("`%s`" % name, feedback_doc, name)

    def test_recipe_links_resolve(self):
        text = read(os.path.join(DOCS, "factory-recipe.md"))
        for target in re.findall(r"\]\((prompts/[^)]+)\)", text):
            self.assertTrue(os.path.isfile(os.path.join(DOCS, target)), target)

    def test_token_pattern_catches_a_fake(self):
        fake = "ghp_" + "x" * 36
        self.assertIsNotNone(TOKEN_RE.search(fake))


if __name__ == "__main__":
    unittest.main()

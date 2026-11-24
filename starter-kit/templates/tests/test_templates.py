"""Checks that the starter-kit templates exist and are well-formed.

Standard library only; no network access.
"""

import re
import unittest
from pathlib import Path

TEMPLATES = Path(__file__).resolve().parent.parent

PROMPTS = ["receptionist.md", "scheduler.md", "follow-up-writer.md"]
PROMPT_SECTIONS = ["## Role", "## Business details", "## Rules",
                   "## Escalation", "## Example"]
LAYOUT_DIRS = ["config", "prompts", "knowledge", "logs", "notes"]

PLACEHOLDER = re.compile(r"\{\{([^{}]*)\}\}")
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
SECRET_HINTS = re.compile(r"(sk-[A-Za-z0-9]{8,}|ghp_[A-Za-z0-9]{8,}|"
                          r"api[_-]?key\s*[:=]|password\s*[:=])", re.I)


def read(path):
    return path.read_text(encoding="utf-8")


def all_markdown():
    return sorted(TEMPLATES.rglob("*.md"))


class TestFilesExist(unittest.TestCase):
    def test_top_level_files(self):
        for name in ["README.md", "CLIENT-README.md", "onboarding-checklist.md"]:
            with self.subTest(name=name):
                self.assertTrue((TEMPLATES / name).is_file())

    def test_prompt_files(self):
        for name in PROMPTS:
            with self.subTest(name=name):
                self.assertTrue((TEMPLATES / "prompts" / name).is_file())

    def test_every_folder_has_readme(self):
        folders = [TEMPLATES] + [p for p in TEMPLATES.rglob("*")
                                 if p.is_dir() and p.name != "__pycache__"]
        for folder in folders:
            with self.subTest(folder=str(folder.relative_to(TEMPLATES))):
                self.assertTrue((folder / "README.md").is_file())

    def test_client_layout(self):
        layout = TEMPLATES / "new-client-layout"
        for name in LAYOUT_DIRS:
            with self.subTest(dir=name):
                self.assertTrue((layout / name).is_dir())


class TestWellFormed(unittest.TestCase):
    def test_markdown_starts_with_heading(self):
        for path in all_markdown():
            with self.subTest(file=str(path.relative_to(TEMPLATES))):
                text = read(path)
                self.assertTrue(text.strip(), "file is empty")
                self.assertTrue(text.startswith("# "), "missing H1 title")

    def test_prompts_have_sections_in_order(self):
        for name in PROMPTS:
            with self.subTest(prompt=name):
                text = read(TEMPLATES / "prompts" / name)
                positions = [text.find(s) for s in PROMPT_SECTIONS]
                self.assertNotIn(-1, positions, "missing a section")
                self.assertEqual(positions, sorted(positions))

    def test_prompts_use_required_placeholders(self):
        for name in PROMPTS:
            with self.subTest(prompt=name):
                found = set(PLACEHOLDER.findall(read(TEMPLATES / "prompts" / name)))
                self.assertIn("BUSINESS_NAME", found)
                self.assertIn("ESCALATION_CONTACT", found)

    def test_placeholders_are_valid(self):
        for path in all_markdown():
            text = read(path)
            with self.subTest(file=str(path.relative_to(TEMPLATES))):
                for name in PLACEHOLDER.findall(text):
                    self.assertRegex(name, r"^[A-Z][A-Z0-9_]*$")
                stripped = PLACEHOLDER.sub("", text)
                self.assertNotIn("{{", stripped, "unbalanced placeholder")
                self.assertNotIn("}}", stripped, "unbalanced placeholder")

    def test_checklist_items(self):
        text = read(TEMPLATES / "onboarding-checklist.md")
        items = re.findall(r"^- \[ \] \S", text, re.M)
        self.assertGreaterEqual(len(items), 10)
        self.assertEqual(re.findall(r"^- \[[xX]\]", text, re.M), [],
                         "template boxes must start unticked")
        sections = re.findall(r"^## \d+\. ", text, re.M)
        self.assertGreaterEqual(len(sections), 3)

    def test_client_readme_is_plain_english(self):
        text = read(TEMPLATES / "CLIENT-README.md")
        for heading in ["## What the assistant does",
                        "## What the assistant will not do",
                        "## What we need from you"]:
            with self.subTest(heading=heading):
                self.assertIn(heading, text)
        self.assertNotIn("```", text, "client guide should avoid code blocks")

    def test_no_emails_or_secrets(self):
        for path in all_markdown() + sorted(TEMPLATES.rglob("*.py")):
            if path == Path(__file__).resolve():
                continue
            text = read(path)
            with self.subTest(file=str(path.relative_to(TEMPLATES))):
                self.assertIsNone(EMAIL.search(text))
                self.assertIsNone(SECRET_HINTS.search(text))


if __name__ == "__main__":
    unittest.main()

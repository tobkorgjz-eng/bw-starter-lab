import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import check_brief  # noqa: E402


def read(name):
    with open(os.path.join(HERE, name), encoding="utf-8") as f:
        return f.read()


class TestExampleAndTemplate(unittest.TestCase):
    def test_example_brief_passes(self):
        self.assertEqual(check_brief.check_brief(read("example-brief.md")), [])

    def test_example_rules_parsed(self):
        text = read("example-brief.md")
        rules = check_brief.parse_rules(check_brief.parse_sections(text))
        self.assertIn("read_inbox", rules["May do alone"])
        self.assertIn("book_appointment", rules["Needs the owner's yes"])
        self.assertIn("issue_refund", rules["Never does"])

    def test_template_has_all_sections_but_is_unfilled(self):
        text = read("brief-template.md")
        problems = check_brief.check_brief(text)
        self.assertFalse(any(p.startswith("missing section") for p in problems))
        self.assertTrue(any("unfilled placeholder" in p for p in problems))

    def test_skill_frontmatter(self):
        text = read("SKILL.md")
        self.assertTrue(text.startswith("---\n"))
        front = text.split("---\n")[1]
        self.assertIn("name: client-intake\n", front)
        self.assertRegex(front, r"description: \S")

    def test_questions_cover_three_rules_lists(self):
        text = read("questions.md")
        for phrase in ("May do alone", "Needs your yes", "Never does"):
            self.assertIn(phrase, text)

    def test_no_banned_word(self):
        for name in ("SKILL.md", "questions.md", "brief-template.md",
                     "example-brief.md"):
            self.assertNotIn("pro" + "of", read(name).lower(), name)


class TestProblems(unittest.TestCase):
    def setUp(self):
        self.good = read("example-brief.md")

    def test_missing_section(self):
        text = self.good.replace("## Never does", "## Not quite")
        problems = check_brief.check_brief(text)
        self.assertIn("missing section: Never does", problems)

    def test_action_on_two_lists(self):
        text = self.good.replace(
            "- `issue_refund` — give a refund",
            "- `book_appointment` — give a refund")
        problems = check_brief.check_brief(text)
        self.assertTrue(any("`book_appointment` is on two lists" in p
                            for p in problems), problems)

    def test_bad_rule_line(self):
        text = self.good.replace("- `read_inbox` — read", "- read_inbox: read")
        problems = check_brief.check_brief(text)
        self.assertTrue(any("rules line not in the form" in p for p in problems))

    def test_uppercase_action_rejected(self):
        text = self.good.replace("`read_inbox`", "`ReadInbox`")
        problems = check_brief.check_brief(text)
        self.assertTrue(any("rules line not in the form" in p for p in problems))

    def test_empty_rules_list(self):
        start = self.good.index("## Never does")
        end = self.good.index("Anything not listed")
        text = self.good[:start] + "## Never does\n\n" + self.good[end:]
        problems = check_brief.check_brief(text)
        self.assertIn("Never does: no rules listed", problems)

    def test_placeholder_found(self):
        text = self.good.replace("Priya Lindqvist on 2026-11-20",
                                 "<name> on <YYYY-MM-DD>")
        problems = check_brief.check_brief(text)
        self.assertTrue(any("<name>" in p for p in problems))

    def test_bad_title(self):
        problems = check_brief.check_brief("# Something else\n")
        self.assertIn("first line should be '# Client brief: <business name>'",
                      problems)

    def test_star_and_numbered_rules_are_read(self):
        text = self.good.replace(
            "- `share_credentials` — reveal passwords or login details.",
            "- `share_credentials` — reveal passwords or login details.\n"
            "* `sign_contract` — agree to a contract.\n"
            "+ `change_permissions_plus` — give anyone more access.\n"
            "1. `change_permissions` — give anyone more access.")
        self.assertEqual(check_brief.check_brief(text), [])
        rules = check_brief.parse_rules(check_brief.parse_sections(text))
        for action in ("sign_contract", "change_permissions_plus",
                       "change_permissions"):
            self.assertIn(action, rules["Never does"])

    def test_bad_star_and_numbered_lines_reported(self):
        text = self.good.replace(
            "- `share_credentials` — reveal passwords or login details.",
            "- `share_credentials` — reveal passwords or login details.\n"
            "* sign_contract: agree to a contract.\n"
            "1. change permissions for anyone")
        problems = check_brief.check_brief(text)
        bad = [p for p in problems if "Never does: rules line not in the form" in p]
        self.assertEqual(len(bad), 2, problems)

    def test_other_text_in_rules_section_reported(self):
        text = self.good.replace(
            "- `share_credentials` — reveal passwords or login details.",
            "- `share_credentials` — reveal passwords or login details.\n"
            "Also never sign contracts.")
        problems = check_brief.check_brief(text)
        self.assertTrue(any("Never does: text that is not a rules line" in p
                            for p in problems), problems)

    def test_limits_widening_warns(self):
        for phrase in ("Refunds of any size may be given without asking.",
                       "Tomas may order parts alone on Saturdays."):
            text = self.good.replace(
                "- Quotes over 150 still need Priya's yes, not Tomas's.",
                "- " + phrase)
            problems = check_brief.check_brief(text)
            self.assertTrue(any(p.startswith("warning: Limits and exceptions")
                                for p in problems), (phrase, problems))

    def test_limits_narrowing_no_warning(self):
        problems = check_brief.check_brief(self.good)
        self.assertFalse(any(p.startswith("warning:") for p in problems))

    def test_skill_names_handoff_command(self):
        self.assertIn("python3 skills/client-rules-file/rules_tool.py "
                      "from-brief brief.md -o answers.json", read("SKILL.md"))

    def test_skill_drafts_topics_message(self):
        text = read("SKILL.md")
        self.assertIn("Draft a short message", text)
        self.assertNotIn("Send the client the list", text)


class TestMain(unittest.TestCase):
    def run_main(self, argv):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = check_brief.main(argv)
        return code, out.getvalue(), err.getvalue()

    def test_ok_exit_zero(self):
        code, out, _ = self.run_main([os.path.join(HERE, "example-brief.md")])
        self.assertEqual(code, 0)
        self.assertIn("OK", out)

    def test_json_output(self):
        code, out, _ = self.run_main(
            [os.path.join(HERE, "example-brief.md"), "--json"])
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertTrue(data["ok"])
        self.assertIn("make_payment", data["rules"]["Never does"])

    def test_problems_exit_one(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "brief.md")
            with open(path, "w", encoding="utf-8") as f:
                f.write("# Client brief: X\n")
            code, out, _ = self.run_main([path])
        self.assertEqual(code, 1)
        self.assertIn("PROBLEM: missing section: Business", out)

    def test_missing_file_exit_two(self):
        code, _, err = self.run_main(["/nonexistent/brief.md"])
        self.assertEqual(code, 2)
        self.assertIn("cannot read", err)

    def test_no_args_exit_two(self):
        code, _, _ = self.run_main([])
        self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()

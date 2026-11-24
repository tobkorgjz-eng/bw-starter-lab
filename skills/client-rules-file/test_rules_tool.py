"""Tests for rules_tool.py. Offline, stdlib only."""

import contextlib
import io
import json
import os
import tempfile
import unittest

import rules_tool

HERE = os.path.dirname(os.path.abspath(__file__))
EXAMPLES = ("maple-lane-bakery", "northgate-bike-repair")


def sample_answers(**changes):
    answers = {
        "business_name": "Pinecrest Plant Shop",
        "owner_name": "Lena Hart",
        "ask_channel": "text message",
        "may_do_alone": ["Answer questions about opening hours"],
        "ask_first": ["Offer a discount"],
        "never_do": ["Take card details in chat"],
    }
    answers.update(changes)
    return answers


def run_cli(*args):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = rules_tool.main(list(args))
    return code, out.getvalue(), err.getvalue()


class BuildTests(unittest.TestCase):
    def test_build_has_all_sections_and_items(self):
        text = rules_tool.build_rules(sample_answers())
        self.assertTrue(text.startswith("# Client rules: Pinecrest Plant Shop"))
        for heading in rules_tool.REQUIRED_SECTIONS:
            self.assertIn(f"## {heading}", text)
        self.assertIn("- Offer a discount", text)
        self.assertIn("Lena Hart", text)

    def test_built_file_passes_check(self):
        errors, warnings = rules_tool.check_rules(
            rules_tool.build_rules(sample_answers()))
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_missing_answer_is_refused(self):
        answers = sample_answers()
        del answers["owner_name"]
        with self.assertRaisesRegex(rules_tool.AnswersError, "owner_name"):
            rules_tool.build_rules(answers)

    def test_empty_owner_is_refused(self):
        with self.assertRaises(rules_tool.AnswersError):
            rules_tool.build_rules(sample_answers(owner_name="  "))

    def test_list_must_be_a_list(self):
        with self.assertRaises(rules_tool.AnswersError):
            rules_tool.build_rules(sample_answers(never_do="delete things"))

    def test_items_are_tidied(self):
        text = rules_tool.build_rules(
            sample_answers(may_do_alone=["  Answer   questions. ", ""]))
        self.assertIn("- Answer questions\n", text)

    def test_optional_fields_appear(self):
        text = rules_tool.build_rules(sample_answers(
            business_type="plant shop", answer_wait="wait", notes="Closed Mondays."))
        self.assertIn("(plant shop)", text)
        self.assertIn("If no answer: wait", text)
        self.assertIn("## Notes", text)

    def test_unknown_fields_are_ignored(self):
        text = rules_tool.build_rules(sample_answers(extra_question="yes"))
        self.assertNotIn("extra_question", text)


class CheckTests(unittest.TestCase):
    def base(self, **changes):
        return rules_tool.build_rules(sample_answers(**changes))

    def assertError(self, text, fragment):
        errors, _ = rules_tool.check_rules(text)
        self.assertTrue(any(fragment in e for e in errors),
                        f"no error containing {fragment!r} in {errors}")

    def test_risky_action_alone_is_error(self):
        self.assertError(self.base(may_do_alone=["Issue a refund"]), "risky action")
        self.assertError(self.base(may_do_alone=["Cancel a booking"]), "cancel")

    def test_risky_word_is_fine_under_ask_first(self):
        errors, _ = rules_tool.check_rules(
            self.base(ask_first=["Issue a refund"]))
        self.assertEqual(errors, [])

    def test_same_item_in_two_lists_is_error(self):
        self.assertError(self.base(ask_first=["Take card details in chat"]),
                         "is in both")

    def test_duplicate_in_same_list_is_warning(self):
        errors, warnings = rules_tool.check_rules(self.base(
            may_do_alone=["Answer questions", "answer questions."]))
        self.assertEqual(errors, [])
        self.assertTrue(any("twice" in w for w in warnings))

    def test_missing_section_is_error(self):
        text = self.base().replace("## Never does", "## Other")
        self.assertError(text, "missing section '## Never does'")

    def test_empty_section_is_error(self):
        text = self.base().replace("- Take card details in chat\n", "")
        self.assertError(text, "has no items")

    def test_wrong_order_is_error(self):
        text = (
            "# Client rules: X\n\n## About\n\n- Owner: A\n\n"
            "## Never does\n\n- a\n\n## May do alone\n\n- b\n\n"
            "## Must ask first\n\n- c\n\n## When unsure\n\n- d\n")
        self.assertError(text, "order")

    def test_bad_title_is_error(self):
        self.assertError(self.base().replace("# Client rules: ", "# Rules "),
                         "first heading")

    def test_owner_required_in_about(self):
        text = self.base().replace("Owner (gives every yes or no)", "Boss")
        self.assertError(text, "Owner")

    def test_banned_wording_is_error(self):
        self.assertError(self.base(notes="We guarantee replies."), "guarantee")
        self.assertError(self.base(notes="Keep proof of orders."), "proof")

    def test_placeholder_is_error(self):
        self.assertError(self.base(notes="TODO ask owner"), "placeholder")
        self.assertError(self.base(owner_name="{{owner}}"), "placeholder")

    def test_long_item_is_warning(self):
        long_item = " ".join(["word"] * 30)
        _, warnings = rules_tool.check_rules(self.base(ask_first=[long_item]))
        self.assertTrue(any("long item" in w for w in warnings))


class ExampleTests(unittest.TestCase):
    def test_examples_pass_check_and_match_build(self):
        for name in EXAMPLES:
            with self.subTest(example=name):
                folder = os.path.join(HERE, "examples", name)
                with open(os.path.join(folder, "answers.json"), encoding="utf-8") as fh:
                    built = rules_tool.build_rules(json.load(fh))
                with open(os.path.join(folder, "RULES.md"), encoding="utf-8") as fh:
                    saved = fh.read()
                self.assertEqual(built, saved, "RULES.md is out of date; rebuild it")
                self.assertEqual(rules_tool.check_rules(saved), ([], []))


BRIEF = os.path.join(HERE, "fixtures", "brief-willowbrook-dog-grooming.md")


def read_brief():
    with open(BRIEF, encoding="utf-8") as fh:
        return fh.read()


class FromBriefTests(unittest.TestCase):
    def test_names_and_lists_are_read(self):
        answers, warnings = rules_tool.answers_from_brief(read_brief())
        self.assertEqual(warnings, [])
        self.assertEqual(answers["business_name"], "Willowbrook Dog Grooming")
        self.assertEqual(answers["owner_name"], "Jun Halloway")
        self.assertTrue(answers["ask_channel"].startswith("text message"))
        self.assertEqual(len(answers["may_do_alone"]), 3)
        self.assertEqual(len(answers["never_do"]), 2)

    def test_needs_owners_yes_becomes_ask_first(self):
        answers, _ = rules_tool.answers_from_brief(read_brief())
        self.assertEqual(answers["ask_first"], [
            "Put a grooming booking on the calendar (book_appointment)",
            "Offer any discount or free extra (offer_discount)",
        ])
        text = rules_tool.build_rules(answers)
        ask = rules_tool.parse_rules(text)[1][rules_tool.SECTION_ASK]
        self.assertIn("Offer any discount or free extra (offer_discount)", ask)

    def test_backup_yes_and_limits_go_to_notes(self):
        answers, _ = rules_tool.answers_from_brief(read_brief())
        self.assertIn("Backup yes: Mira Stone", answers["notes"])
        self.assertIn("After 18:00: drafts only.", answers["notes"])

    def test_brief_to_rules_passes_check(self):
        answers, _ = rules_tool.answers_from_brief(read_brief())
        errors, _ = rules_tool.check_rules(rules_tool.build_rules(answers))
        self.assertEqual(errors, [])

    def test_unconfirmed_brief_warns(self):
        text = read_brief().replace("Status: confirmed", "Status: draft")
        _, warnings = rules_tool.answers_from_brief(text)
        self.assertTrue(any("confirmed" in w for w in warnings))

    def test_missing_owner_or_section_is_refused(self):
        text = read_brief().replace("- Owner / final yes: Jun Halloway, owner\n", "")
        with self.assertRaisesRegex(rules_tool.AnswersError, "Owner / final yes"):
            rules_tool.answers_from_brief(text)
        text = read_brief().replace("## Never does", "## Other")
        with self.assertRaisesRegex(rules_tool.AnswersError, "Never does"):
            rules_tool.answers_from_brief(text)

    def test_not_a_brief_is_refused(self):
        with self.assertRaises(rules_tool.AnswersError):
            rules_tool.answers_from_brief("# Something else\n")

    def test_plain_items_are_kept(self):
        self.assertEqual(rules_tool._brief_item("Answer the phone"), "Answer the phone")

    def test_risky_brief_item_alone_is_caught(self):
        text = read_brief().replace(
            "- `draft_reply`", "- `issue_refund` — give a refund.\n- `draft_reply`", 1)
        answers, _ = rules_tool.answers_from_brief(text)
        errors, _ = rules_tool.check_rules(rules_tool.build_rules(answers))
        self.assertTrue(any("risky action" in e for e in errors))


class CliTests(unittest.TestCase):
    def test_from_brief_then_build_then_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            answers = os.path.join(tmp, "answers.json")
            rules = os.path.join(tmp, "RULES.md")
            self.assertEqual(run_cli("from-brief", BRIEF, "-o", answers)[0], 0)
            with open(answers, encoding="utf-8") as fh:
                self.assertEqual(json.load(fh)["owner_name"], "Jun Halloway")
            self.assertEqual(run_cli("build", answers, "-o", rules)[0], 0)
            self.assertEqual(run_cli("check", rules)[0], 0)

    def test_from_brief_bad_input_exit_2(self):
        self.assertEqual(run_cli("from-brief", "/nonexistent/brief.md")[0], 2)

    def test_build_then_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            answers = os.path.join(tmp, "answers.json")
            rules = os.path.join(tmp, "RULES.md")
            with open(answers, "w", encoding="utf-8") as fh:
                json.dump(sample_answers(), fh)
            self.assertEqual(run_cli("build", answers, "-o", rules)[0], 0)
            code, out, _ = run_cli("check", rules)
            self.assertEqual(code, 0)
            self.assertIn("OK", out)

    def test_check_reports_errors_with_exit_1(self):
        with tempfile.TemporaryDirectory() as tmp:
            rules = os.path.join(tmp, "RULES.md")
            with open(rules, "w", encoding="utf-8") as fh:
                fh.write(rules_tool.build_rules(
                    sample_answers(may_do_alone=["Cancel a booking"])))
            code, out, _ = run_cli("check", rules)
            self.assertEqual(code, 1)
            self.assertIn("error: risky action under 'May do alone': "
                          "'Cancel a booking' (mentions cancel)", out)

    def test_missing_files_exit_2(self):
        self.assertEqual(run_cli("check", "/nonexistent/RULES.md")[0], 2)
        self.assertEqual(run_cli("build", "/nonexistent/answers.json")[0], 2)

    def test_bad_json_exit_2(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "answers.json")
            with open(path, "w", encoding="utf-8") as fh:
                fh.write("{not json")
            code, _, err = run_cli("build", path)
            self.assertEqual(code, 2)
            self.assertIn("error:", err)


if __name__ == "__main__":
    unittest.main()

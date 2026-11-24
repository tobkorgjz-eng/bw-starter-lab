import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr

import check_rules as cr

HERE = os.path.dirname(os.path.abspath(__file__))

SAMPLE = """# Rules
Intro text with `not_a_rule` in it.

## May do alone
- `read_inbox` - read mail
* `tag_message` - sort mail

## Needs the owner's yes
- `send_email` - send mail

## Never does
- `delete_records` - delete data
"""


class ParseRulesTest(unittest.TestCase):
    def test_sections(self):
        rules = cr.parse_rules(SAMPLE)
        self.assertEqual(rules, {
            "read_inbox": cr.ALONE,
            "tag_message": cr.ALONE,
            "send_email": cr.NEEDS_YES,
            "delete_records": cr.NEVER,
        })

    def test_intro_backticks_ignored(self):
        self.assertNotIn("not_a_rule", cr.parse_rules(SAMPLE))

    def test_conflict_raises(self):
        text = SAMPLE + "\n## May do alone\n- `delete_records` - oops\n"
        with self.assertRaises(cr.RulesError):
            cr.parse_rules(text)

    def test_empty_raises(self):
        with self.assertRaises(cr.RulesError):
            cr.parse_rules("# Nothing here\n")

    def test_shipped_rules_file(self):
        rules = cr.load_rules(os.path.join(HERE, "RULES.md"))
        cats = set(rules.values())
        self.assertEqual(cats, {cr.ALONE, cr.NEEDS_YES, cr.NEVER})
        self.assertEqual(rules["read_inbox"], cr.ALONE)
        self.assertEqual(rules["send_email"], cr.NEEDS_YES)
        self.assertEqual(rules["share_credentials"], cr.NEVER)


class CheckActionTest(unittest.TestCase):
    def setUp(self):
        self.rules = cr.parse_rules(SAMPLE)

    def test_alone_allowed(self):
        self.assertEqual(cr.check_action(self.rules, "read_inbox")[0], cr.ALLOW)

    def test_needs_yes_without_approval(self):
        self.assertEqual(cr.check_action(self.rules, "send_email")[0], cr.ASK)

    def test_needs_yes_with_approval(self):
        self.assertEqual(cr.check_action(self.rules, "send_email", True)[0], cr.ALLOW)

    def test_never_blocked_even_if_approved(self):
        self.assertEqual(cr.check_action(self.rules, "delete_records", True)[0], cr.BLOCK)

    def test_unknown_asks(self):
        self.assertEqual(cr.check_action(self.rules, "order_flowers")[0], cr.ASK)
        self.assertEqual(cr.check_action(self.rules, "order_flowers", True)[0], cr.ALLOW)


class CheckPlanTest(unittest.TestCase):
    def setUp(self):
        self.rules = cr.parse_rules(SAMPLE)

    def test_mixed_plan(self):
        plan = ["read_inbox", {"action": "send_email", "owner_approved": True},
                "delete_records", " tag_message "]
        verdicts = [r["verdict"] for r in cr.check_plan(self.rules, plan)]
        self.assertEqual(verdicts, [cr.ALLOW, cr.ALLOW, cr.BLOCK, cr.ALLOW])

    def test_all_allowed(self):
        res = cr.check_plan(self.rules, ["read_inbox", "tag_message"])
        self.assertTrue(cr.all_allowed(res))
        res = cr.check_plan(self.rules, ["read_inbox", "send_email"])
        self.assertFalse(cr.all_allowed(res))

    def test_empty_plan_ok(self):
        self.assertEqual(cr.check_plan(self.rules, []), [])

    def test_bad_plans(self):
        for bad in [{"action": "x"}, [42], [{"owner_approved": True}], [""],
                    [{"action": "send_email", "owner_approved": "yes"}]]:
            with self.assertRaises(cr.RulesError):
                cr.check_plan(self.rules, bad)

    def test_format_summary(self):
        out = cr.format_results(cr.check_plan(self.rules, ["read_inbox", "delete_records"]))
        self.assertIn("Summary: 1 allow, 0 ask, 1 block", out)


class MainTest(unittest.TestCase):
    def _run(self, plan, rules_path=None):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "plan.json")
            with open(p, "w", encoding="utf-8") as fh:
                if isinstance(plan, str):
                    fh.write(plan)
                else:
                    json.dump(plan, fh)
            argv = [p] + (["--rules", rules_path] if rules_path else [])
            out, err = io.StringIO(), io.StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                code = cr.main(argv)
            return code, out.getvalue(), err.getvalue()

    def test_exit_zero_when_all_allowed(self):
        code, out, _ = self._run(["read_inbox", "draft_reply"])
        self.assertEqual(code, 0)
        self.assertIn("Summary: 2 allow", out)

    def test_exit_one_when_blocked(self):
        code, out, _ = self._run(["read_inbox", "make_payment"])
        self.assertEqual(code, 1)
        self.assertIn("BLOCK", out)

    def test_exit_two_on_bad_json(self):
        code, _, err = self._run("{not json")
        self.assertEqual(code, 2)
        self.assertIn("error", err)

    def test_exit_two_on_missing_rules(self):
        code, _, _ = self._run(["read_inbox"], rules_path="/nonexistent/RULES.md")
        self.assertEqual(code, 2)

    def test_example_plan(self):
        code_out = io.StringIO()
        with redirect_stdout(code_out):
            code = cr.main([os.path.join(HERE, "example_plan.json")])
        self.assertEqual(code, 1)
        self.assertIn("Summary: 3 allow, 2 ask, 1 block", code_out.getvalue())


if __name__ == "__main__":
    unittest.main()

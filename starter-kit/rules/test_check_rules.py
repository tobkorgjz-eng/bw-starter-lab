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

    def test_needs_yes_with_owner_approval(self):
        self.assertEqual(
            cr.check_action(self.rules, "send_email", {"send_email"})[0], cr.ALLOW)

    def test_approval_is_per_action(self):
        self.assertEqual(
            cr.check_action(self.rules, "send_email", {"other_action"})[0], cr.ASK)

    def test_never_blocked_even_if_owner_approved(self):
        self.assertEqual(
            cr.check_action(self.rules, "delete_records", {"delete_records"})[0], cr.BLOCK)

    def test_unknown_asks(self):
        self.assertEqual(cr.check_action(self.rules, "order_flowers")[0], cr.ASK)
        self.assertEqual(
            cr.check_action(self.rules, "order_flowers", {"order_flowers"})[0], cr.ALLOW)



class CanonicalNameTest(unittest.TestCase):
    def test_variants(self):
        for raw in ["delete_records", "Delete_Records", "delete-records",
                    "DELETE-RECORDS", "delete records", " Delete__Records ",
                    "delete - records", "_delete_records_"]:
            with self.subTest(raw=raw):
                self.assertEqual(cr.canonical_name(raw), "delete_records")

    def test_rules_file_names_are_canonical(self):
        rules = cr.parse_rules("## Never does\n- `Delete-Records` - x\n")
        self.assertEqual(rules, {"delete_records": cr.NEVER})

    def test_spelling_variants_conflict(self):
        text = "## May do alone\n- `send_email`\n## Never does\n- `Send-Email`\n"
        with self.assertRaises(cr.RulesError):
            cr.parse_rules(text)


class NeverCannotBeRespelledTest(unittest.TestCase):
    VARIANTS = ["Delete_Records", "delete-records", "DELETE RECORDS",
                "delete__records"]

    def setUp(self):
        self.rules = cr.parse_rules(SAMPLE)

    def test_variants_block(self):
        for name in self.VARIANTS:
            with self.subTest(name=name):
                self.assertEqual(cr.check_action(self.rules, name)[0], cr.BLOCK)

    def test_variants_block_even_when_approved(self):
        for name in self.VARIANTS:
            for approval in (name, "delete_records", "Delete-Records"):
                with self.subTest(name=name, approval=approval):
                    res = cr.check_plan(self.rules, [name], [approval])
                    self.assertEqual(res[0]["verdict"], cr.BLOCK)
                    res = cr.check_plan(self.rules, [{"action": name,
                                                      "owner_approved": True}],
                                        [approval])
                    self.assertEqual(res[0]["verdict"], cr.BLOCK)

    def test_other_sections_match_variants(self):
        self.assertEqual(cr.check_action(self.rules, "Read-Inbox")[0], cr.ALLOW)
        self.assertEqual(cr.check_action(self.rules, "SEND EMAIL")[0], cr.ASK)
        res = cr.check_plan(self.rules, ["Send-Email"], ["send_email"])
        self.assertEqual(res[0]["verdict"], cr.ALLOW)
        self.assertEqual(res[0]["action"], "Send-Email")  # shown as written


class OneYesOneTimeTest(unittest.TestCase):
    def setUp(self):
        self.rules = cr.parse_rules(SAMPLE)

    def verdicts(self, plan, approvals):
        return [r["verdict"] for r in cr.check_plan(self.rules, plan, approvals)]

    def test_one_yes_covers_one_occurrence(self):
        self.assertEqual(self.verdicts(["send_email"] * 3, ["send_email"]),
                         [cr.ALLOW, cr.ASK, cr.ASK])

    def test_used_up_yes_is_explained(self):
        res = cr.check_plan(self.rules, ["send_email", "send_email"], ["send_email"])
        self.assertIn("already used", res[1]["reason"])
        self.assertNotIn("already used", res[0]["reason"])

    def test_count_matches_yeses(self):
        self.assertEqual(self.verdicts(["send_email"] * 3, ["send_email"] * 2),
                         [cr.ALLOW, cr.ALLOW, cr.ASK])
        self.assertEqual(self.verdicts(["send_email"] * 2, ["send_email"] * 3),
                         [cr.ALLOW, cr.ALLOW])

    def test_spelling_variants_share_one_yes(self):
        self.assertEqual(self.verdicts(["send_email", "Send-Email"], ["SEND_EMAIL"]),
                         [cr.ALLOW, cr.ASK])

    def test_unlisted_action_counts_too(self):
        self.assertEqual(self.verdicts(["order_flowers"] * 2, ["order_flowers"]),
                         [cr.ALLOW, cr.ASK])

    def test_alone_and_never_use_no_yes(self):
        plan = ["read_inbox", "delete_records", "send_email"]
        self.assertEqual(self.verdicts(plan, ["read_inbox", "delete_records",
                                              "send_email"]),
                         [cr.ALLOW, cr.BLOCK, cr.ALLOW])
        self.assertEqual(self.verdicts(["delete_records", "send_email"],
                                       ["send_email"]),
                         [cr.BLOCK, cr.ALLOW])

    def test_caller_approvals_not_changed(self):
        approvals = ["send_email"]
        self.verdicts(["send_email"], approvals)
        self.assertEqual(approvals, ["send_email"])
        self.assertEqual(self.verdicts(["send_email"], approvals), [cr.ALLOW])


class CheckPlanTest(unittest.TestCase):
    def setUp(self):
        self.rules = cr.parse_rules(SAMPLE)

    def test_self_approval_in_plan_is_ignored(self):
        # The bot marks its own needs-yes action as approved; with no owner
        # approval input it must still be ASK.
        plan = [{"action": "send_email", "owner_approved": True}]
        res = cr.check_plan(self.rules, plan)
        self.assertEqual(res[0]["verdict"], cr.ASK)
        self.assertIn("ignored", res[0]["reason"])
        self.assertFalse(cr.all_allowed(res))

    def test_self_approval_other_keys_ignored(self):
        for key in ("approved", "approval"):
            res = cr.check_plan(self.rules, [{"action": "send_email", key: True}])
            self.assertEqual(res[0]["verdict"], cr.ASK)

    def test_self_approval_on_unlisted_action_ignored(self):
        res = cr.check_plan(self.rules, [{"action": "order_flowers", "owner_approved": True}])
        self.assertEqual(res[0]["verdict"], cr.ASK)

    def test_owner_approval_outside_plan_allows(self):
        res = cr.check_plan(self.rules, [{"action": "send_email"}], ["send_email"])
        self.assertEqual(res[0]["verdict"], cr.ALLOW)

    def test_mixed_plan(self):
        plan = ["read_inbox", {"action": "send_email"},
                "delete_records", " tag_message "]
        verdicts = [r["verdict"] for r in cr.check_plan(self.rules, plan, ["send_email"])]
        self.assertEqual(verdicts, [cr.ALLOW, cr.ALLOW, cr.BLOCK, cr.ALLOW])

    def test_all_allowed(self):
        res = cr.check_plan(self.rules, ["read_inbox", "tag_message"])
        self.assertTrue(cr.all_allowed(res))
        res = cr.check_plan(self.rules, ["read_inbox", "send_email"])
        self.assertFalse(cr.all_allowed(res))

    def test_empty_plan_ok(self):
        self.assertEqual(cr.check_plan(self.rules, []), [])

    def test_bad_plans(self):
        for bad in [{"action": "x"}, [42], [{"owner_approved": True}], [""]]:
            with self.assertRaises(cr.RulesError):
                cr.check_plan(self.rules, bad)

    def test_bad_approvals(self):
        for bad in [{"send_email": True}, "send_email", [42], [""]]:
            with self.assertRaises(cr.RulesError):
                cr.check_plan(self.rules, ["send_email"], bad)

    def test_format_summary(self):
        out = cr.format_results(cr.check_plan(self.rules, ["read_inbox", "delete_records"]))
        self.assertIn("Summary: 1 allow, 0 ask, 1 block", out)


class MainTest(unittest.TestCase):
    def _run(self, plan, rules_path=None, approvals=None, extra=()):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "plan.json")
            with open(p, "w", encoding="utf-8") as fh:
                if isinstance(plan, str):
                    fh.write(plan)
                else:
                    json.dump(plan, fh)
            argv = [p] + (["--rules", rules_path] if rules_path else [])
            if approvals is not None:
                a = os.path.join(d, "approvals.json")
                with open(a, "w", encoding="utf-8") as fh:
                    if isinstance(approvals, str):
                        fh.write(approvals)
                    else:
                        json.dump(approvals, fh)
                argv += ["--approvals", a]
            argv += list(extra)
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

    def test_self_approved_plan_still_asks(self):
        code, out, _ = self._run([{"action": "send_email", "owner_approved": True}])
        self.assertEqual(code, 1)
        self.assertIn("ASK", out)

    def test_owner_approvals_file(self):
        code, out, _ = self._run([{"action": "send_email"}], approvals=["send_email"])
        self.assertEqual(code, 0)

    def test_owner_approve_flag(self):
        code, _, _ = self._run(["send_email", "issue_refund"],
                               extra=["--approve", "send_email", "--approve", "issue_refund"])
        self.assertEqual(code, 0)

    def test_exit_two_on_bad_approvals_file(self):
        code, _, err = self._run(["send_email"], approvals="{not json")
        self.assertEqual(code, 2)
        self.assertIn("error", err)

    def test_exit_two_on_bad_json(self):
        code, _, err = self._run("{not json")
        self.assertEqual(code, 2)
        self.assertIn("error", err)

    def test_exit_two_on_missing_rules(self):
        code, _, _ = self._run(["read_inbox"], rules_path="/nonexistent/RULES.md")
        self.assertEqual(code, 2)

    def test_example_plan(self):
        out = io.StringIO()
        with redirect_stdout(out):
            code = cr.main([os.path.join(HERE, "example_plan.json")])
        self.assertEqual(code, 1)
        self.assertIn("Summary: 2 allow, 3 ask, 1 block", out.getvalue())

    def test_example_plan_with_owner_approvals(self):
        out = io.StringIO()
        with redirect_stdout(out):
            code = cr.main([os.path.join(HERE, "example_plan.json"),
                            "--approvals", os.path.join(HERE, "example_owner_approvals.json")])
        self.assertEqual(code, 1)
        text = out.getvalue()
        self.assertIn("Summary: 3 allow, 2 ask, 1 block", text)
        # issue_refund was self-approved in the plan but not by the owner.
        self.assertRegex(text, r"ASK\s+issue_refund")


    def test_cli_one_approve_flag_covers_one_send(self):
        code, out, _ = self._run(["send_email", "send_email"],
                                 extra=["--approve", "send_email"])
        self.assertEqual(code, 1)
        self.assertIn("Summary: 1 allow, 1 ask, 0 block", out)
        code, out, _ = self._run(["send_email", "send_email"],
                                 extra=["--approve", "send_email",
                                        "--approve", "send_email"])
        self.assertEqual(code, 0, out)

    def test_cli_flag_and_file_add_up(self):
        code, out, _ = self._run(["send_email", "send_email"],
                                 approvals=["send_email"],
                                 extra=["--approve", "send_email"])
        self.assertEqual(code, 0, out)

    def test_cli_respelled_never_is_blocked(self):
        for name in ["Delete_Records", "delete-records"]:
            with self.subTest(name=name):
                code, out, _ = self._run([name], extra=["--approve", name])
                self.assertEqual(code, 1)
                self.assertIn("Summary: 0 allow, 0 ask, 1 block", out)


if __name__ == "__main__":
    unittest.main()

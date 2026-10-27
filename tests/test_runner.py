import json
import tempfile
import unittest
from pathlib import Path

from examples.toy_env import ToyEnv
from holdout_controls import cli
from holdout_controls.runner import run


def by_key(report):
    return {(r.task, r.control): r for r in report.results}


class RunnerTest(unittest.TestCase):
    def test_do_nothing_on_the_buggy_grader_is_a_finding(self):
        r = by_key(run(ToyEnv()))
        self.assertEqual(r[("sum-buggy", "do-nothing")].status, "finding")
        self.assertEqual(r[("sum-buggy", "do-nothing")].reward, 1.0)

    def test_the_fixed_grader_has_no_findings(self):
        r = by_key(run(ToyEnv()))
        self.assertEqual(r[("sum-fixed", "do-nothing")].status, "ok")
        self.assertEqual(r[("sum-fixed", "reference")].status, "ok")

    def test_a_reference_that_fails_is_a_finding(self):
        class Broken(ToyEnv):
            def reference(self, task_id, workspace):
                (workspace / "answer.txt").write_text("6\n")

        r = by_key(run(Broken(), tasks=["sum-fixed"]))
        self.assertEqual(r[("sum-fixed", "reference")].status, "finding")

    def test_no_reference_means_skipped_not_failed(self):
        class NoRef:
            def tasks(self):
                return ["t"]

            def setup(self, task_id, workspace):
                pass

            def grade(self, task_id, workspace):
                return 0.0

        r = by_key(run(NoRef()))
        self.assertEqual(r[("t", "reference")].status, "skipped")
        self.assertEqual(r[("t", "do-nothing")].status, "ok")

    def test_a_crashing_grader_is_an_error_never_a_pass(self):
        class Crash(ToyEnv):
            def grade(self, task_id, workspace):
                raise RuntimeError("boom")

        report = run(Crash(), tasks=["sum-fixed"])
        self.assertTrue(all(r.status == "error" for r in report.results))
        self.assertTrue(all(r.passed is None for r in report.results))


class CliTest(unittest.TestCase):
    def test_exit_code_and_json_report(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "report.json"
            code = cli.main(["run", "examples.toy_env:ToyEnv", "--json", str(out)])
            self.assertEqual(code, 1)
            data = json.loads(out.read_text())
            self.assertEqual(data["counts"]["finding"], 1)

    def test_bad_spec_exits_2(self):
        self.assertEqual(cli.main(["run", "nope"]), 2)


if __name__ == "__main__":
    unittest.main()

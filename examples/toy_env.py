"""A two-task toy environment for trying holdout-controls.

Each task asks the agent to write the sum of two numbers to ``answer.txt``.

The grader for ``sum-buggy`` has a common bug: setup() writes a placeholder ``answer.txt``
and the grader only checks that the file exists, so a run that does nothing scores 1.0.
``sum-fixed`` checks the value.

    holdout-controls run examples.toy_env:ToyEnv
"""

from pathlib import Path

PROBLEMS = {"sum-buggy": (2, 3), "sum-fixed": (2, 3)}


class ToyEnv:
    def tasks(self):
        return list(PROBLEMS)

    def setup(self, task_id, workspace: Path):
        a, b = PROBLEMS[task_id]
        (workspace / "task.txt").write_text(f"Write {a} + {b} to answer.txt\n")
        (workspace / "answer.txt").write_text("TODO\n")

    def reference(self, task_id, workspace: Path):
        a, b = PROBLEMS[task_id]
        (workspace / "answer.txt").write_text(f"{a + b}\n")

    def grade(self, task_id, workspace: Path) -> float:
        answer = workspace / "answer.txt"
        if task_id == "sum-buggy":
            return 1.0 if answer.exists() else 0.0
        a, b = PROBLEMS[task_id]
        return 1.0 if answer.read_text().strip() == str(a + b) else 0.0

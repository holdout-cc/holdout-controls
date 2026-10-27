"""Run each control on each task, in a fresh workspace, and compare against what it should get."""

from __future__ import annotations

import shutil
import tempfile
import traceback
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable, List, Optional, Sequence

from .adapter import Environment, has_reference, pass_threshold
from .controls import DEFAULT_CONTROLS, Control


@dataclass
class Result:
    task: str
    control: str
    expect_pass: bool
    reward: Optional[float]
    passed: Optional[bool]
    status: str  # ok, finding, skipped, error
    detail: str = ""


@dataclass
class Report:
    threshold: float
    results: List[Result] = field(default_factory=list)

    @property
    def findings(self) -> List[Result]:
        return [r for r in self.results if r.status == "finding"]

    @property
    def errors(self) -> List[Result]:
        return [r for r in self.results if r.status == "error"]

    def to_dict(self) -> dict:
        counts = {s: sum(r.status == s for r in self.results) for s in ("ok", "finding", "skipped", "error")}
        return {"threshold": self.threshold, "counts": counts, "results": [asdict(r) for r in self.results]}


def run_one(env: Environment, task_id: str, control: Control, threshold: float) -> Result:
    if control.needs_reference and not has_reference(env):
        return Result(task_id, control.name, control.expect_pass, None, None, "skipped",
                      "the environment has no reference()")
    workspace = Path(tempfile.mkdtemp(prefix="holdout-controls-"))
    try:
        env.setup(task_id, workspace)
        control.act(env, task_id, workspace)
        reward = float(env.grade(task_id, workspace))
    except Exception:  # noqa: BLE001 - a crash is reported, never treated as a pass
        return Result(task_id, control.name, control.expect_pass, None, None, "error",
                      traceback.format_exc(limit=3).strip())
    finally:
        shutil.rmtree(workspace, ignore_errors=True)
    passed = reward >= threshold
    if passed == control.expect_pass:
        return Result(task_id, control.name, control.expect_pass, reward, passed, "ok")
    detail = ("rewarded a run that did not do the task" if passed
              else "the reference solution did not pass")
    return Result(task_id, control.name, control.expect_pass, reward, passed, "finding", detail)


def run(env: Environment, controls: Sequence[Control] = DEFAULT_CONTROLS,
        tasks: Optional[Iterable[str]] = None) -> Report:
    threshold = pass_threshold(env)
    report = Report(threshold=threshold)
    for task_id in (list(tasks) if tasks is not None else list(env.tasks())):
        for control in controls:
            report.results.append(run_one(env, task_id, control, threshold))
    return report

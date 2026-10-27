"""Controls: scripted runs with a known right answer.

A control acts on the workspace the way an agent would, then the environment grades it.
``expect_pass`` says what a sound grader must do with the result: the reference solution
must pass, and a run that didn't do the task must not.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable


@dataclass(frozen=True)
class Control:
    name: str
    expect_pass: bool
    description: str
    act: Callable[[object, str, Path], None]
    needs_reference: bool = False


def _nothing(env: object, task_id: str, workspace: Path) -> None:
    pass


def _reference(env: object, task_id: str, workspace: Path) -> None:
    env.reference(task_id, workspace)  # type: ignore[attr-defined]


DO_NOTHING = Control(
    name="do-nothing",
    expect_pass=False,
    description="Leaves the workspace exactly as setup() left it.",
    act=_nothing,
)

REFERENCE = Control(
    name="reference",
    expect_pass=True,
    description="Applies the environment's own reference solution.",
    act=_reference,
    needs_reference=True,
)

DEFAULT_CONTROLS = (REFERENCE, DO_NOTHING)

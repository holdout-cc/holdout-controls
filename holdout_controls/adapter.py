"""The interface an environment implements so its tasks can be run under controls.

An environment needs three things:

- ``tasks()``: the task ids to check.
- ``setup(task_id, workspace)``: put the task's starting files in ``workspace``, an empty
  directory the runner creates for each run.
- ``grade(task_id, workspace)``: grade whatever is in ``workspace`` now and return the reward
  as a float.

``reference(task_id, workspace)`` is optional. If the environment has one, it should apply
the known-good solution to ``workspace``; the runner uses it as the positive control.

The workspace is the agent's side of the task: everything a control does, it does there,
the way an agent would. ``grade`` is the environment's own grader, unchanged.
"""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Iterable, Optional, Protocol, runtime_checkable


@runtime_checkable
class Environment(Protocol):
    def tasks(self) -> Iterable[str]: ...

    def setup(self, task_id: str, workspace: Path) -> None: ...

    def grade(self, task_id: str, workspace: Path) -> float: ...


def has_reference(env: object) -> bool:
    return callable(getattr(env, "reference", None))


def load(spec: str) -> Environment:
    """Load an environment from ``module:attribute``.

    The attribute may be an environment object, or a callable that returns one.
    """
    module_name, sep, attr = spec.partition(":")
    if not sep or not module_name or not attr:
        raise ValueError(f"expected module:attribute, got {spec!r}")
    obj = getattr(importlib.import_module(module_name), attr)
    if isinstance(obj, type) or (callable(obj) and not isinstance(obj, Environment)):
        obj = obj()  # a class or a factory
    env = obj
    if not isinstance(env, Environment):
        raise TypeError(f"{spec} has no tasks(), setup() and grade()")
    return env


def pass_threshold(env: object) -> float:
    """The reward at or above which a run counts as a pass. Defaults to 1.0."""
    value: Optional[float] = getattr(env, "pass_threshold", None)
    return 1.0 if value is None else float(value)

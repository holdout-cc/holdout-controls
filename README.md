# holdout-controls

Run scripted controls against an RL environment's grader, and find the tasks that reward a run
that didn't do the work.

A control is a scripted "agent" whose right answer is known in advance. The reference solution
must pass. A run that does nothing must not. If a grader gives credit to a control that should
fail, that task can be passed without being solved, and an RL policy trained on it can learn the
shortcut.

No model calls, no API keys: the same environment gives the same report every time, so it can
run in CI on every change to a task.

> Status: early. v0 has the runner, the adapter interface and two controls (reference and
> do-nothing). Cheat controls for the hacks in
> [reward-hack-patterns](https://github.com/holdout-cc/reward-hack-patterns), a Harbor task
> adapter and a GitHub Action are next.

## Try it

Python 3.9 or later, no dependencies.

```
git clone https://github.com/holdout-cc/holdout-controls
cd holdout-controls
python -m holdout_controls.cli run examples.toy_env:ToyEnv
```

```
ok       sum-buggy                      reference    reward=1
finding  sum-buggy                      do-nothing   reward=1  (rewarded a run that did not do the task)
ok       sum-fixed                      reference    reward=1
ok       sum-fixed                      do-nothing   reward=0

1 finding(s), 0 error(s), 3 ok, 0 skipped
```

The exit code is 0 with no findings, 1 with findings and 2 on errors, so it can gate a CI job.
`--json report.json` writes the full report.

## Connect your environment

Write a small adapter with three methods (a fourth is optional):

| Method | What it does |
|---|---|
| `tasks()` | The task ids to check. |
| `setup(task_id, workspace)` | Put the task's starting files in `workspace`, an empty directory created for each run. |
| `grade(task_id, workspace)` | Run your grader on what is in `workspace` now and return the reward. |
| `reference(task_id, workspace)` | Optional. Apply the known-good solution; used as the positive control. |

Then run `holdout-controls run your_module:YourEnv`. A run counts as a pass at reward 1.0, or at
`pass_threshold` if your adapter sets one. See [`examples/toy_env.py`](examples/toy_env.py).

A crash in setup or grading is reported as an error, never as a pass.

## Tests

```
python -m unittest discover -s tests -t .
```

## License

MIT. Made by [Holdout](https://holdout.cc), which audits RL environments for reward hacks.

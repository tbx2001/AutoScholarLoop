# AutoScholarLoop Workspace Contract

External coding agents should treat each run directory as the only mutable workspace.

## Read Inputs

- `inputs/seed.json`
- `00_field_context/field_map.md`
- `01_decision/executor_brief.md`
- `02_execution/RESULTS_ANALYSIS.md` when present
- existing files under `code/`

## Write Outputs

- `code/experiments/run_experiment.py`
- `code/methods/proposed_method.py`
- `code/experiments/config.json`
- `code/experiments/result.json` when runnable
- `code/run_commands.json`
- `agent_tasks/.../agent_result.json`

## Evidence Levels

- `real_result`: real dataset, baseline, metrics, and result artifact.
- `smoke_result`: runnable sanity check only.
- `scaffold_only`: code scaffold created but not validated with a run.
- `blocked`: missing dependency, data, credentials, or compute prevents execution.

---
name: autoscholar-execution-bridge
description: Implement or refine AutoScholarLoop S02 experiment workspaces from generated agent task packages. Use when working on AutoScholarLoop `agent_tasks/*/task.json` files, creating or updating `code/experiments/run_experiment.py`, `code/methods/proposed_method.py`, `code/run_commands.json`, and `agent_result.json` while preserving the run workspace contract.
---

# AutoScholar Execution Bridge

Use this skill to complete an AutoScholarLoop S02 external coding-agent task.

## Inputs

Start from a generated task package:

```text
agent_tasks/
  S02_RXX_execution_bridge/
    TASK.md
    task.json
    expected_result_schema.json
```

Treat `task.json` as the source of truth. The `workspace` field is the run root,
not the repository root.

Read task-relevant inputs only:

   - `00_field_context/field_map.md`
   - `01_decision/executor_brief.md`
   - existing `code/` files
   - prior `02_execution/` reports when present

For the full workspace contract, read
`references/workspace-contract.md` only when path or evidence-level details are
needed.

## Workflow

### Phase 1: Interpret The Task

Extract from `task.json`:

- current S02 round and focus;
- selected idea;
- execution plan and commands;
- allowed and forbidden write roots;
- required outputs.

If required context files are missing, continue with available information and
record the gap in `agent_result.json`.

### Phase 2: Implement The Workspace Code

Create or refine:

   - `code/experiments/run_experiment.py`
   - `code/methods/proposed_method.py`
   - `code/experiments/config.json`
   - `code/run_commands.json`

Prefer a minimal runnable experiment scaffold over broad speculative code. Keep
all run parameters configurable through argparse or JSON config. Save outputs as
JSON so AutoScholarLoop can inspect them later.

### Phase 3: Validate Locally When Safe

Run the command from `code/run_commands.json` or `task.json` if it only depends
on local standard-library code and available dependencies.

Classify the evidence level:

- `real_result`: real dataset, real baseline, real metric, and result artifact.
- `smoke_result`: code ran on a toy or placeholder sanity input.
- `scaffold_only`: files were written but not executed.
- `blocked`: missing data, credentials, hardware, dependency, or external repo.

### Phase 4: Write The Agent Result

Write `agent_result.json` in the same directory as `task.json`. Use relative
paths from the run workspace.

Then run the bundled validator when Python is available:

```bash
python skills/autoscholar-execution-bridge/scripts/validate_agent_result.py path/to/task.json
```

## Boundaries

- Do not modify project source directories such as `src/`, `web/`, `docs/`, `configs/`, or `templates/`.
- Do not run destructive shell commands.
- Do not claim empirical support unless a real dataset, baseline, metric, and result file exist.
- If only a generated scaffold or smoke test exists, set `claim_support` to `scaffold_only` or `smoke_result`.
- If the task requires missing datasets, credentials, GPUs, or external repositories, set `status` to `blocked` and explain the blocker.

## Agent Result Contract

Write `agent_result.json` with this shape:

```json
{
  "schema": "autoscholarloop.agent_result.v1",
  "status": "completed",
  "changed_files": [
    "code/experiments/run_experiment.py"
  ],
  "commands": [
    "python code/experiments/run_experiment.py --config code/experiments/config.json --output code/experiments/result.json"
  ],
  "evidence_files": [
    "code/experiments/result.json"
  ],
  "claim_support": "smoke_result",
  "notes": "Short factual summary."
}
```

Allowed `status` values: `completed`, `blocked`, `failed`.

Allowed `claim_support` values: `real_result`, `smoke_result`, `scaffold_only`, `blocked`.

## Quality Checklist

- The changed files are inside `allowed_write_roots`.
- `code/run_commands.json` contains the commands needed to reproduce the check.
- Any `result.json` clearly distinguishes placeholder data from real evidence.
- `agent_result.json` names every changed file and evidence file.
- Unsupported empirical claims are labeled as missing evidence, not promoted.

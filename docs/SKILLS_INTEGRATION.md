# Agent Integration

The repository can expose agent-callable wrappers that operate on the same
workspace contract as the Python pipeline. These wrappers are generated from New
AI Scientist's native capability contracts; they are not direct copies of any
external skill files.

## Implemented Agent Bridge

The first supported bridge is `--execution-backend agent-task`.

This backend does not invoke Codex, ClaudeCode, or any local coding agent
directly. Instead, each S02 execution round writes an auditable task package:

```text
agent_tasks/
  S02_R01_execution_bridge/
    TASK.md
    task.json
    expected_result_schema.json
```

External coding agents can use the repository skill at
`skills/autoscholar-execution-bridge/SKILL.md` to complete the task and write
`agent_result.json`.

The skill includes a small validator:

```powershell
python skills/autoscholar-execution-bridge/scripts/validate_agent_result.py `
  runs/demo/agent_tasks/S02_R01_execution_bridge/task.json
```

This keeps the Python/Web orchestrator safe by default while still making the
workspace contract skill-friendly.

## Planned Agent Wrappers

- `nars-brief-normalizer`: normalize ideas and references.
- `nars-direction-workshop`: expand directions and run committee debate.
- `nars-frontier-probe`: search literature and kill near-duplicates.
- `autoscholar-execution-bridge`: implemented as a repository skill template for S02 coding tasks.
- `nars-evidence-writer`: draft paper sections from evidence.
- `nars-review-loop`: review and create revision tasks.
- `nars-release-builder`: package final paper and artifacts.

## Wrapper Contract

Each wrapper receives:

- workspace path;
- stage name;
- artifact paths from dependencies;
- allowed tools;
- safety limits.

Each wrapper must write:

- a JSON artifact;
- a Markdown summary;
- manifest update or return data that the Python runner records.

## Codex And ClaudeCode Direction

The skills should not hide decisions in chat. They should write durable files
that the Python orchestrator can validate and resume.

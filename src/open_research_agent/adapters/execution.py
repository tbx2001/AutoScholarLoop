from __future__ import annotations

import json
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class ExecutionBackend(ABC):
    @abstractmethod
    def execute(self, workspace: Path, plan: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError


class DryRunExecutionBackend(ExecutionBackend):
    def execute(self, workspace: Path, plan: dict[str, Any]) -> dict[str, Any]:
        return {
            "backend": "dry_run",
            "status": "completed",
            "runs": [
                {
                    "name": "dry_run_protocol_check",
                    "command": None,
                    "return_code": 0,
                    "summary": "No command executed; plan was converted into a traceable pseudo-run.",
                }
            ],
        }


class ShellExecutionBackend(ExecutionBackend):
    def __init__(self, commands: list[str] | None = None, timeout: int = 7200):
        self.commands = commands or []
        self.timeout = timeout

    def execute(self, workspace: Path, plan: dict[str, Any]) -> dict[str, Any]:
        commands = self.commands or plan.get("commands", [])
        if not commands and (workspace / "code" / "experiments" / "run_experiment.py").exists():
            commands = [
                "python code/experiments/run_experiment.py "
                "--config code/experiments/config.json "
                "--output code/experiments/result.json"
            ]
        run_dir = workspace / "logs" / "shell_runs"
        run_dir.mkdir(parents=True, exist_ok=True)
        runs = []
        for index, command in enumerate(commands, start=1):
            result = subprocess.run(
                command,
                cwd=str(workspace),
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
            log_path = run_dir / f"run_{index:02d}.json"
            record = {
                "name": f"shell_run_{index:02d}",
                "command": command,
                "return_code": result.returncode,
                "stdout": result.stdout[-4000:],
                "stderr": result.stderr[-4000:],
            }
            log_path.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
            runs.append(record)
        return {"backend": "shell", "status": "completed", "runs": runs}


class AgentTaskExecutionBackend(ExecutionBackend):
    """Emit an auditable task package for an external coding agent or skill."""

    backend_name = "agent_task"

    def execute(self, workspace: Path, plan: dict[str, Any]) -> dict[str, Any]:
        round_id = int(plan.get("execution_round") or 1)
        task_dir = workspace / "agent_tasks" / f"S02_R{round_id:02d}_execution_bridge"
        task_dir.mkdir(parents=True, exist_ok=True)

        task_rel_dir = f"agent_tasks/S02_R{round_id:02d}_execution_bridge"
        task = {
            "schema": "autoscholarloop.agent_task.v1",
            "skill": "autoscholar-execution-bridge",
            "stage": "S02",
            "round": round_id,
            "workspace": str(workspace),
            "focus": plan.get("focus", ""),
            "selected_idea": plan.get("selected_idea", ""),
            "plan": plan,
            "inputs": {
                "field_map": "00_field_context/field_map.md",
                "executor_brief": "01_decision/executor_brief.md",
                "previous_execution": "02_execution/RESULTS_ANALYSIS.md",
                "generated_code": "02_execution/GENERATED_CODE.md",
            },
            "allowed_write_roots": ["code", "02_execution", task_rel_dir],
            "forbidden_write_roots": ["src", "web", "docs", "configs", "templates"],
            "required_outputs": [
                "code/experiments/run_experiment.py",
                "code/methods/proposed_method.py",
                "code/run_commands.json",
                f"{task_rel_dir}/agent_result.json",
            ],
            "safety": {
                "do_not_modify_project_source": True,
                "no_destructive_commands": True,
                "network_requires_user_approval": True,
                "report_real_vs_smoke_results": True,
            },
        }
        expected_result = {
            "schema": "autoscholarloop.agent_result.v1",
            "status": "completed|blocked|failed",
            "changed_files": ["relative/path"],
            "commands": ["command used to run or validate the experiment"],
            "evidence_files": ["relative/path/to/result.json"],
            "claim_support": "real_result|smoke_result|scaffold_only|blocked",
            "notes": "short summary of what the external agent did",
        }

        task_json = task_dir / "task.json"
        task_md = task_dir / "TASK.md"
        schema_json = task_dir / "expected_result_schema.json"
        task_json.write_text(json.dumps(task, indent=2, ensure_ascii=False), encoding="utf-8")
        schema_json.write_text(json.dumps(expected_result, indent=2, ensure_ascii=False), encoding="utf-8")
        task_md.write_text(_agent_task_markdown(task), encoding="utf-8")

        task_files = [str(task_json), str(task_md), str(schema_json)]
        return {
            "backend": self.backend_name,
            "status": "task_created",
            "task_dir": str(task_dir),
            "task_files": task_files,
            "runs": [
                {
                    "name": f"agent_task_S02_R{round_id:02d}",
                    "command": None,
                    "return_code": None,
                    "summary": "External coding agent task package created; no local command executed.",
                }
            ],
        }


def build_execution_backend(name: str, commands: list[str] | None = None) -> ExecutionBackend:
    if name == "dry-run":
        return DryRunExecutionBackend()
    if name == "shell":
        return ShellExecutionBackend(commands=commands)
    if name == "agent-task":
        return AgentTaskExecutionBackend()
    raise ValueError(f"Unsupported execution backend: {name}")


def _agent_task_markdown(task: dict[str, Any]) -> str:
    required = "\n".join(f"- `{path}`" for path in task["required_outputs"])
    allowed = "\n".join(f"- `{path}/`" for path in task["allowed_write_roots"])
    forbidden = "\n".join(f"- `{path}/`" for path in task["forbidden_write_roots"])
    return (
        "# S02 External Coding Agent Task\n\n"
        "Use the `autoscholar-execution-bridge` skill from this repository to implement or refine "
        "the experiment scaffold for this workspace.\n\n"
        f"- Workspace: `{task['workspace']}`\n"
        f"- Stage: `{task['stage']}`\n"
        f"- Round: `{task['round']}`\n"
        f"- Focus: {task.get('focus', '')}\n"
        f"- Selected idea: `{task.get('selected_idea', '')}`\n\n"
        "## Allowed Write Paths\n\n"
        f"{allowed}\n\n"
        "## Do Not Modify\n\n"
        f"{forbidden}\n\n"
        "## Required Outputs\n\n"
        f"{required}\n\n"
        "## Result Contract\n\n"
        "Write `agent_result.json` in this task directory using `expected_result_schema.json`. "
        "Mark `claim_support` as `real_result`, `smoke_result`, `scaffold_only`, or `blocked`.\n\n"
        "## Safety\n\n"
        "- Do not run destructive commands.\n"
        "- Do not modify project source code outside the run workspace.\n"
        "- Do not present smoke-test outputs as empirical research evidence.\n"
    )

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class SkillSpec:
    stage: str
    name: str
    path: str
    purpose: str
    outputs: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


STAGE_SKILLS: dict[str, SkillSpec] = {
    "S00": SkillSpec(
        stage="S00",
        name="autoscholar-field-archive",
        path="skills/autoscholar-field-archive/SKILL.md",
        purpose="Normalize the seed, references, uploaded notes, and field context into auditable archive artifacts.",
        outputs=("field_map.md", "paper_cards.md", "evidence_bank.md"),
    ),
    "S01": SkillSpec(
        stage="S01",
        name="autoscholar-direction-review",
        path="skills/autoscholar-direction-review/SKILL.md",
        purpose="Generate, criticize, rank, and select research directions without promoting weak novelty claims.",
        outputs=("IDEA_REPORT.md", "chosen_direction.md", "executor_brief.md"),
    ),
    "S02": SkillSpec(
        stage="S02",
        name="autoscholar-experiment-runner",
        path="skills/autoscholar-experiment-runner/SKILL.md",
        purpose="Implement experiment scaffolds, run safe checks, and report what evidence the execution actually supports.",
        outputs=("GENERATED_CODE.md", "RESULTS_ANALYSIS.md", "EXPERIMENT_AUDIT.md"),
    ),
    "S03": SkillSpec(
        stage="S03",
        name="autoscholar-manuscript-builder",
        path="skills/autoscholar-manuscript-builder/SKILL.md",
        purpose="Turn verified evidence into a format-aware manuscript draft and claim-evidence table.",
        outputs=("PAPER_PLAN.md", "claim_evidence_table.md", "paper/final_draft.md"),
    ),
    "S04": SkillSpec(
        stage="S04",
        name="autoscholar-quality-gate",
        path="skills/autoscholar-quality-gate/SKILL.md",
        purpose="Audit novelty, citations, reproducibility, and claim support before release.",
        outputs=("CITATION_AUDIT.md", "final_gate.md", "release/README.md"),
    ),
}


def stage_skill_context(stage: str) -> dict[str, object]:
    skill = STAGE_SKILLS.get(stage)
    return skill.to_dict() if skill else {}


def all_skill_context() -> dict[str, dict[str, object]]:
    return {stage: skill.to_dict() for stage, skill in STAGE_SKILLS.items()}


def skills_manifest_markdown() -> str:
    lines = [
        "# AutoScholarLoop Skill Manifest",
        "",
        "These repository skills support the automatic Python pipeline. They are optional agent-facing",
        "instructions and do not replace the default end-to-end S00-S04 workflow.",
        "",
        "| Stage | Skill | Purpose | Key Outputs |",
        "|---|---|---|---|",
    ]
    for skill in STAGE_SKILLS.values():
        outputs = ", ".join(f"`{item}`" for item in skill.outputs)
        lines.append(f"| {skill.stage} | `{skill.name}` | {skill.purpose} | {outputs} |")
    return "\n".join(lines) + "\n"

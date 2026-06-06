from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
import time

from agent_workflow_bench.catalog import load_task


CODEX_PATH = Path(r"C:\Users\jie13\AppData\Local\OpenAI\Codex\bin\7dea4a003bc76627\codex.exe")


@dataclass(slots=True)
class RunnerResult:
    ok: bool
    status: str
    stdout: str
    stderr: str
    candidate_path: str
    duration_seconds: float
    command: list[str]


def build_executor_prompt(task_path: str | Path) -> str:
    task = load_task(task_path)
    lines = [
        f"Task: {task.title}",
        "",
        f"Objective: {task.objective}",
    ]
    if task.success_criteria:
        lines.extend(["", "Success criteria:"])
        lines.extend([f"- {item}" for item in task.success_criteria])
    if task.constraints:
        lines.extend(["", "Constraints:"])
        lines.extend([f"- {item}" for item in task.constraints])
    if task.allowed_tools:
        lines.extend(["", "Allowed tools:"])
        lines.extend([f"- {item}" for item in task.allowed_tools])
    if task.hints:
        lines.extend(["", "Hints:"])
        lines.extend([f"- {item}" for item in task.hints])
    lines.extend(
        [
            "",
            "Instructions:",
            "- Produce a concise plain-text answer only.",
            "- Do not modify files.",
            "- If the workspace does not contain enough evidence, say what is missing.",
        ]
    )
    return "\n".join(lines)


def run_codex_prompt(
    prompt: str,
    cwd: str | Path,
    output_path: str | Path,
    timeout_seconds: int = 120,
) -> RunnerResult:
    if not CODEX_PATH.exists():
        raise FileNotFoundError(f"Codex CLI not found: {CODEX_PATH}")

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        str(CODEX_PATH),
        "exec",
        "--skip-git-repo-check",
        "--ephemeral",
        "--sandbox",
        "read-only",
        "-c",
        'model_reasoning_effort="minimal"',
        "--output-last-message",
        str(output_file),
        "-C",
        str(Path(cwd).resolve()),
        prompt,
    ]
    start = time.time()
    try:
        completed = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=timeout_seconds,
        )
        return RunnerResult(
            ok=completed.returncode == 0 and output_file.exists(),
            status="completed" if completed.returncode == 0 and output_file.exists() else "failed",
            stdout=completed.stdout,
            stderr=completed.stderr,
            candidate_path=str(output_file),
            duration_seconds=round(time.time() - start, 3),
            command=cmd,
        )
    except subprocess.TimeoutExpired as exc:
        return RunnerResult(
            ok=False,
            status="timeout",
            stdout=exc.stdout or "",
            stderr=exc.stderr or "",
            candidate_path=str(output_file),
            duration_seconds=round(time.time() - start, 3),
            command=cmd,
        )


def run_codex_executor(
    task_path: str | Path,
    cwd: str | Path,
    output_path: str | Path,
    timeout_seconds: int = 120,
    extra_instructions: str | None = None,
) -> RunnerResult:
    prompt = build_executor_prompt(task_path)
    if extra_instructions:
        prompt = f"{prompt}\n\nPlanning context:\n{extra_instructions[:3000]}"
    return run_codex_prompt(prompt, cwd, output_path, timeout_seconds=timeout_seconds)

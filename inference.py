"""
Inference Script — Git Merge Conflict Resolution Environment
=============================================================
Runs a frozen LLM against the environment to produce baseline scores.

MANDATORY ENV VARS:
    API_BASE_URL    — LLM endpoint (default: HF router)
    MODEL_NAME      — model identifier (default: Qwen2.5-72B-Instruct)
    HF_TOKEN        — Hugging Face API key (required, no default)

OPTIONAL ENV VARS:
    LOCAL_IMAGE_NAME — Docker image name for from_docker_image() mode.
                       When unset, connects to the deployed HF Space.

STDOUT FORMAT:
    [START] task=<task> env=git-merge-conflict-env model=<model>
    [STEP]  step=<n> action=<action> reward=<0.00> done=<true|false> error=<msg|null>
    [END]   success=<true|false> steps=<n> score=<s.sss> rewards=<r1,r2,...>
"""

import asyncio
import os
import textwrap
from typing import List, Optional

from openai import OpenAI

from git_merge_conflict_env import MergeConflictAction, MergeConflictEnv

# ── Required environment variables ──────────────────────────
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN")

# Optional — only used when launching the env from a local Docker image.
LOCAL_IMAGE_NAME = os.getenv("LOCAL_IMAGE_NAME")

if HF_TOKEN is None:
    raise ValueError("HF_TOKEN environment variable is required")

# ── Constants ───────────────────────────────────────────────
ENV_NAME = "git-merge-conflict-env"
MAX_STEPS = 10
TEMPERATURE = 0.0
MAX_TOKENS = 2000

SYSTEM_PROMPT = textwrap.dedent("""\
    You are an expert software engineer resolving git merge conflicts.
    You will be given a file with conflict markers (<<<<<<< ======= >>>>>>>).
    Your job is to produce the correctly merged file content.

    Rules:
    - Remove ALL conflict markers (<<<<<<< ======= >>>>>>>)
    - Merge both sides intelligently based on the context provided
    - Output ONLY the resolved file content, nothing else
    - Do not add explanations, comments, or markdown formatting
    - Preserve the original code style and indentation
""")


# ── Logging helpers (EXACT FORMAT REQUIRED) ─────────────────
def log_start(task: str, model: str) -> None:
    print(f"[START] task={task} env={ENV_NAME} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    done_str = str(done).lower()
    error_str = error if error else "null"
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={done_str} error={error_str}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    success_str = str(success).lower()
    print(
        f"[END] success={success_str} steps={steps} score={score:.3f} rewards={rewards_str}",
        flush=True,
    )


# ── LLM call ────────────────────────────────────────────────
def get_resolution(client: OpenAI, file_content: str, branch_info: str, filename: str) -> str:
    """Ask the LLM to resolve a merge conflict."""
    user_prompt = textwrap.dedent(f"""\
        Resolve the following git merge conflict in file '{filename}'.

        Context: {branch_info}

        File with conflicts:
        ```
        {file_content}
        ```

        Output ONLY the resolved file content. No explanations.
    """)

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            stream=False,
        )
        text = (completion.choices[0].message.content or "").strip()
        # Strip markdown code fences if present
        if text.startswith("```"):
            lines = text.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines)
        return text if text else ""
    except Exception as exc:
        print(f"[DEBUG] Model request failed: {exc}", flush=True)
        return ""


# ── Main loop ───────────────────────────────────────────────
async def run_task(client: OpenAI, env: MergeConflictEnv, task_id: str) -> float:
    """Run a single task and return the final score."""
    log_start(task=task_id, model=MODEL_NAME)

    rewards: List[float] = []
    steps_taken = 0

    try:
        result = await env.reset(task_id=task_id)
        obs = result.observation

        for step in range(1, MAX_STEPS + 1):
            if result.done:
                break

            # Get resolution from LLM (run sync OpenAI call in a thread so the
            # asyncio event loop stays free to handle WebSocket keepalive pings)
            resolution = await asyncio.to_thread(
                get_resolution,
                client,
                obs.file_content,
                obs.branch_info,
                obs.filename,
            )

            action_str = f"resolve({obs.filename})"

            # Step
            result = await env.step(MergeConflictAction(resolved_content=resolution))
            obs = result.observation
            reward = result.reward if result.reward is not None else 0.0
            rewards.append(reward)
            steps_taken = step

            error_str = obs.last_action_error if hasattr(obs, "last_action_error") else None
            log_step(step=step, action=action_str, reward=reward, done=result.done, error=error_str)

            if result.done:
                break

        final_score = rewards[-1] if rewards else 0.0
        success = final_score >= 0.5
        log_end(success=success, steps=steps_taken, score=final_score, rewards=rewards)
        return final_score

    except Exception as exc:
        print(f"[DEBUG] Task {task_id} failed: {exc}", flush=True)
        log_end(success=False, steps=steps_taken, score=0.0, rewards=rewards)
        return 0.0


def make_env() -> MergeConflictEnv:
    """Construct the environment client.

    Mode selection (matches the OpenEnv submission checklist):
      1. If LOCAL_IMAGE_NAME is set → launch the env from that Docker image.
      2. Otherwise → connect over HTTP to the deployed HF Space.
    """
    if LOCAL_IMAGE_NAME:
        return MergeConflictEnv.from_docker_image(LOCAL_IMAGE_NAME)
    return MergeConflictEnv(base_url="https://swastikr-git-merge-conflict-env.hf.space")


async def main() -> None:
    client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)
    env = make_env()

    scores = {}
    try:
        for task_id in ["easy", "medium", "hard", "expert", "nightmare"]:
            score = await run_task(client, env, task_id)
            scores[task_id] = score
    finally:
        await env.close()

    print("\n--- Baseline Scores ---", flush=True)
    for task_id, score in scores.items():
        print(f"  {task_id}: {score:.2f}", flush=True)
    avg = sum(scores.values()) / len(scores)
    print(f"  average: {avg:.2f}", flush=True)


if __name__ == "__main__":
    asyncio.run(main())

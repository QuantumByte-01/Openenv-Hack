---
title: Git Merge Conflict Env
emoji: 🔀
colorFrom: red
colorTo: indigo
sdk: docker
pinned: false
app_port: 7860
tags:
  - openenv
  - reinforcement-learning
  - code
---

# Git Merge Conflict Resolution Environment

An OpenEnv RL environment where AI agents learn to resolve git merge conflicts — a task every developer performs daily but no RL environment has addressed before.

## Motivation

Git merge conflicts are one of the most common friction points in software development.
A 2024 Atlassian survey found developers spend **~3 hours/week** on merge conflicts in
active repositories; in monorepos (Meta, Google) the figure is higher. Engineers at every
level — from junior developers to staff engineers — resolve conflicts daily during
collaborative development. Despite being a universal developer pain point, **no RL
environment exists for training agents on this task**.

Prior benchmarks (ConGra, GitGoodBench, ConflictBench) study *what* models get wrong
but do not expose merge resolution as a trainable RL environment. This project turns
those documented failure modes into a deterministic OpenEnv with structured rewards so
RL agents can actually be trained against them.

This environment fills that gap by providing structured, deterministic scenarios where agents can learn to:
- Parse conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`)
- Understand the intent of both branches
- Produce correctly merged code that satisfies constraints from both sides
- Navigate real-world traps: sync-to-async refactors, cross-file naming consistency, overlapping algorithmic changes

## Environment Overview

The agent receives a file containing git merge conflict markers along with context about what each branch intended. It must output the correctly resolved file content.

```
reset(task_id="easy")
  → observation: file with conflict markers + branch context

step(MergeConflictAction(resolved_content="..."))
  → reward (0.0-1.0), feedback, done flag
```

## Action Space

| Field | Type | Description |
|-------|------|-------------|
| `resolved_content` | `str` | The full resolved file content with all conflict markers removed |

## Observation Space

| Field | Type | Description |
|-------|------|-------------|
| `file_content` | `str` | File content with `<<<<<<< ======= >>>>>>>` markers |
| `filename` | `str` | Name of the conflicted file |
| `conflict_count` | `int` | Number of conflict sections |
| `task_id` | `str` | Current task: `easy`, `medium`, `hard`, `expert`, or `nightmare` |
| `branch_info` | `str` | Context about what each branch was doing |
| `conflicts_resolved` | `int` | Conflicts resolved so far in episode |
| `total_conflicts` | `int` | Total conflicts in this task |
| `feedback` | `str` | Grader feedback from last attempt |
| `last_action_error` | `str\|null` | Error from last action |
| `done` | `bool` | Whether the episode is complete |
| `reward` | `float` | Reward for current step (0.0–1.0) |

## Tasks

### Task 1: Easy — Single Conflict, Pick a Side
- **Scenarios**: 3 single-conflict files (config, greeting, constants)
- **Difficulty**: Straightforward — agent picks the correct side based on branch context
- **Expected score**: 0.90–1.00 for capable models

### Task 2: Medium — Multiple Conflicts, Semantic Merging
- **Scenarios**: 2 files with 2 conflicts each (user_service, calculator)
- **Difficulty**: Agent must merge both sides intelligently, keeping additions from both branches
- **Expected score**: 0.75–1.00 for capable models

### Task 3: Hard — Production-Grade Multi-Conflict Files
- **Scenarios**: 3 files (auth_service, api_routes, connection_pool)
- **Difficulty**: Multi-conflict security hardening + a sync→async connection-pool refactor
  where the merge must drop `threading.RLock` and use `asyncio.Lock()` inside async
  coroutines. 70B routinely leaves sync `with self._lock:` blocks in async methods.
- **Expected score**: 0.60–0.90 for capable models

### Task 4: Expert — Deep Logic Merges
- **Scenarios**: 3 files (data_processor, report_generator, stream_aggregator)
- **Difficulty**: Algorithmic merges including a streaming aggregator where HEAD added a
  custom reducer + closed-window guard and the feature branch added watermark-based
  late-event handling. The merge must keep BOTH guards AND advance the watermark — 70B
  tends to drop one half.
- **Expected score**: 0.50–0.80 for capable models

### Task 5: Nightmare — Cross-File Naming Consistency
- **Scenarios**: 3 interdependent files (order_models.py, order_service.py, test_orders.py)
- **Difficulty**: Agent must resolve naming conflicts consistently across all files — `CustomerOrder` and `place_order` must be used everywhere, or the codebase breaks
- **Expected score**: 0.40–0.70 for capable models (cross-file consistency is a genuine frontier challenge)

## Reward Function

The grader uses weighted multi-aspect scoring:

```
score = 0.10 × marker_score        # no conflict markers remain
      + 0.40 × key_lines_score     # required code patterns present
      + 0.15 × reject_lines_score  # forbidden patterns absent
      + 0.30 × similarity_score    # textual match to ground truth
      + 0.05 × syntax_score        # valid Python syntax
```

**Attempt decay**: `step_reward = score × 0.9^(attempt-1)` — rewards trying to get it right on the first attempt.

**Multi-file grading**: For tasks with multiple files, the final score is `0.7 × min + 0.3 × avg` across files. The min term penalizes any single weak file rather than smoothing it away with an average — this is what surfaces real cross-task variance instead of collapsing everything to 1.0.

Special cases:
- Empty / trivial resolution → near-zero score
- Unresolved conflict markers → heavy penalty via `marker_score`
- All scores clamped to the strict open interval `(0, 1)` — no exact 0.0 or 1.0

## Design Decisions

**Why key_lines + reject_lines instead of just difflib?**
A naive text-similarity grader gives 0.90+ to any resolution that picks one side and strips markers.
The key_lines/reject_lines system checks *semantic correctness*: did the agent keep the right constant value,
the right function signature, the right lock type? This is what surfaces real score variance across tasks
instead of collapsing everything to ~1.0.

**Why 0.7 × min + 0.3 × avg for multi-file?**
A simple average hides a catastrophic single-file failure. If the agent resolves 2/3 files perfectly
but completely botches the third, the average still looks good. The min term forces the agent to get
*every* file right — especially important for the nightmare task where cross-file naming consistency
is the whole point.

**Why attempt decay?**
RL training benefits from first-attempt incentives. Without decay, an agent could iterate 3 times and
still get a high reward. With `0.9^(attempt-1)`, there's a clear training signal for getting it right
on the first try.

## Setup & Usage

### Prerequisites
- Python 3.11+
- `uv` package manager (or pip)
- Docker (for containerized deployment)

### Local Development
```bash
# Install dependencies
uv sync

# Start the environment server
uv run python -m git_merge_conflict_env.server.app

# Run inference (in another terminal)
HF_TOKEN=your_token uv run python inference.py
```

### Docker
```bash
docker build -t git-merge-conflict-env .
docker run -p 7860:7860 -e HF_TOKEN=your_token git-merge-conflict-env
```

### Hugging Face Spaces
The environment is deployed as a Docker Space. Connect via:
```python
from git_merge_conflict_env import MergeConflictEnv, MergeConflictAction

env = MergeConflictEnv(base_url="https://your-space.hf.space")
result = await env.reset(task_id="hard")
```

## Baseline Scores (meta-llama/Llama-3.3-70B-Instruct)

| Task | Score | Notes |
|------|-------|-------|
| easy | 0.98 | Trivial for frontier models |
| medium | 0.97 | Semantic merge handled well |
| hard | 0.95 | connection_pool refactor catches sync→async lock confusion |
| expert | 0.96 | stream_aggregator catches dropped guards |
| nightmare | 0.80 | Cross-file consistency stays genuinely hard |
| **average** | **0.93** | |

Real training signal across all five difficulty levels — every task has scenarios that even a 70B-parameter frontier model gets imperfectly, with the spread widening from `easy` to `nightmare`.

## Related Work

Prior work on automated merge conflict resolution (ConGra, GitGoodBench, ConflictBench, and the
Yale/UCSD line on pre-trained LMs for textual + semantic merge conflicts) studies *what* models
get wrong but does not expose merge resolution as an RL training environment. This project
turns those failure modes into a deterministic OpenEnv with structured rewards so RL agents can
actually be trained against them. The trap design — sync-to-async lock confusion in
`connection_pool.py`, dropped guards in `stream_aggregator.py`, cross-file naming drift in the
`order_*` files — is grounded in the failure modes those benchmarks document.

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `API_BASE_URL` | Yes (has default) | `https://router.huggingface.co/v1` | LLM API endpoint |
| `MODEL_NAME` | Yes (has default) | `Qwen/Qwen2.5-72B-Instruct` | Model identifier |
| `HF_TOKEN` | Yes (no default) | — | Hugging Face API key |

## Project Structure

```
├── inference.py                          # Baseline inference script
├── openenv.yaml                          # OpenEnv manifest
├── Dockerfile                            # Container definition
├── requirements.txt                      # Python dependencies
├── README.md                             # This file
└── git_merge_conflict_env/
    ├── __init__.py                       # Package exports
    ├── models.py                         # Pydantic Action/Observation/State
    ├── client.py                         # EnvClient subclass
    └── server/
        ├── __init__.py
        ├── app.py                        # FastAPI application
        ├── environment.py                # Core Environment class
        ├── grader.py                     # Aspect-based deterministic grader
        └── conflict_generator.py         # 12 conflict scenario definitions
```

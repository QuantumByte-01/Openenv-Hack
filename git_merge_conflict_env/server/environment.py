"""Core Environment for Git Merge Conflict Resolution."""

import uuid
from typing import Optional

from openenv.core.env_server import Environment

try:
    from ..models import MergeConflictAction, MergeConflictObservation, MergeConflictState
except ImportError:
    from git_merge_conflict_env.models import MergeConflictAction, MergeConflictObservation, MergeConflictState

from .conflict_generator import get_task, get_all_task_ids, ConflictScenario
from .grader import grade_resolution, grade_multi_file

# ── Tuning constants ──────────────────────────────────────
ADVANCE_THRESHOLD = 0.85   # minimum score to move to next file
MAX_ATTEMPTS = 3           # max attempts per task
ATTEMPT_DECAY = 0.9        # reward *= ATTEMPT_DECAY^(attempt-1)


class MergeConflictEnvironment(Environment[MergeConflictAction, MergeConflictObservation, MergeConflictState]):
    """RL environment where agents resolve git merge conflicts."""

    SUPPORTS_CONCURRENT_SESSIONS = False

    def __init__(self):
        super().__init__()
        self._state = MergeConflictState()
        self._task = None
        self._current_scenario_idx = 0
        self._resolutions = []  # collected resolutions for multi-file tasks
        self._rewards = []
        self._file_attempts = 0  # attempts on current file (resets when advancing)

    def reset(self, seed=None, episode_id=None, **kwargs) -> MergeConflictObservation:
        """Reset environment with a task. Pass task_id='easy'|'medium'|'hard'|'expert'|'nightmare' in kwargs."""
        task_id = kwargs.get("task_id", "easy")
        if task_id not in get_all_task_ids():
            task_id = "easy"

        self._task = get_task(task_id)
        self._current_scenario_idx = 0
        self._resolutions = []
        self._rewards = []
        self._file_attempts = 0

        total_conflicts = sum(s.conflict_count for s in self._task.scenarios)

        self._state = MergeConflictState(
            episode_id=episode_id or str(uuid.uuid4()),
            step_count=0,
            task_id=task_id,
            current_file_idx=0,
            conflicts_resolved=0,
            total_conflicts=total_conflicts,
            score=0.0,
            attempts=0,
            max_attempts=MAX_ATTEMPTS,
        )

        scenario = self._task.scenarios[0]
        return self._build_observation(scenario, feedback=f"Task: {self._task.description}")

    def step(self, action: MergeConflictAction, timeout_s=None, **kwargs) -> MergeConflictObservation:
        """Process an agent's resolution attempt."""
        self._state.step_count += 1
        self._state.attempts += 1
        self._file_attempts += 1

        if self._task is None:
            return MergeConflictObservation(
                done=True,
                reward=0.0,
                last_action_error="Environment not initialized. Call reset() first.",
            )

        scenario = self._task.scenarios[self._current_scenario_idx]

        # Validate action — empty submission is a destructive no-op, penalise but
        # don't consume an attempt (so the grader still sees the real submissions)
        if not action.resolved_content or not action.resolved_content.strip():
            self._state.attempts -= 1
            self._file_attempts -= 1
            return self._build_observation(
                scenario,
                reward=-0.1,
                feedback="Empty resolution submitted. Provide the resolved file content.",
                error="Empty resolution — attempt not counted, but reward penalised.",
            )

        # Grade the resolution
        result = grade_resolution(
            action.resolved_content,
            scenario.ground_truth,
            scenario.conflict_count,
            key_lines=scenario.key_lines,
            reject_lines=scenario.reject_lines,
            filename=scenario.filename,
        )

        # Apply attempt decay: reward *= ATTEMPT_DECAY^(attempt-1)
        step_reward = result.score * (ATTEMPT_DECAY ** (self._state.attempts - 1))
        self._rewards.append(step_reward)

        # Update resolved count
        resolved_this_step = scenario.conflict_count - result.conflicts_remaining
        self._state.conflicts_resolved += max(0, resolved_this_step)

        # Move to next file if score is good enough or per-file attempts exhausted
        if result.score >= ADVANCE_THRESHOLD or self._file_attempts >= self._state.max_attempts:
            self._resolutions.append(action.resolved_content)
            self._current_scenario_idx += 1
            self._state.current_file_idx = self._current_scenario_idx
            self._file_attempts = 0  # reset attempt counter for next file

        # Check if all scenarios are done
        if self._current_scenario_idx >= len(self._task.scenarios):
            final_score = self._compute_final_score()
            self._state.score = final_score
            return MergeConflictObservation(
                done=True,
                reward=round(max(0.0, min(1.0, final_score)), 3),
                feedback=f"All files resolved. Final score: {final_score:.2f}. {result.feedback}",
                conflicts_resolved=self._state.conflicts_resolved,
                total_conflicts=self._state.total_conflicts,
                task_id=self._state.task_id,
            )

        # Still more files/attempts to go
        next_scenario = self._task.scenarios[self._current_scenario_idx]
        return self._build_observation(
            next_scenario,
            reward=round(max(0.0, min(1.0, step_reward)), 2),
            feedback=result.feedback,
        )

    @property
    def state(self) -> MergeConflictState:
        return self._state

    def _build_observation(
        self,
        scenario: ConflictScenario,
        reward: float = 0.0,
        feedback: str = "",
        error: Optional[str] = None,
    ) -> MergeConflictObservation:
        return MergeConflictObservation(
            file_content=scenario.conflicted_content,
            filename=scenario.filename,
            conflict_count=scenario.conflict_count,
            task_id=self._state.task_id,
            branch_info=scenario.branch_info,
            conflicts_resolved=self._state.conflicts_resolved,
            total_conflicts=self._state.total_conflicts,
            feedback=feedback,
            done=False,
            reward=round(max(0.0, min(1.0, reward)), 3),
            last_action_error=error,
        )

    def _compute_final_score(self) -> float:
        """Compute the final episode score."""
        if not self._rewards:
            return 0.0
        # For multi-file: grade all resolutions together
        if len(self._task.scenarios) > 1 and len(self._resolutions) == len(self._task.scenarios):
            result = grade_multi_file(
                self._resolutions,
                [s.ground_truth for s in self._task.scenarios],
                [s.conflict_count for s in self._task.scenarios],
                key_lines_list=[s.key_lines for s in self._task.scenarios],
                reject_lines_list=[s.reject_lines for s in self._task.scenarios],
                filenames=[s.filename for s in self._task.scenarios],
            )
            return round(max(0.0, min(1.0, result.score)), 3)
        # Single file or incomplete: average of step rewards
        avg = sum(self._rewards) / len(self._rewards)
        return round(max(0.0, min(1.0, avg)), 3)

"""EnvClient for the Git Merge Conflict environment."""

from typing import Any, Dict

from openenv.core.env_client import EnvClient
from openenv.core.client_types import StepResult

from .models import MergeConflictAction, MergeConflictObservation, MergeConflictState


class MergeConflictEnv(EnvClient[MergeConflictAction, MergeConflictObservation, MergeConflictState]):
    """Client to interact with the Git Merge Conflict environment."""

    def _step_payload(self, action: MergeConflictAction) -> Dict[str, Any]:
        return {"resolved_content": action.resolved_content}

    def _parse_result(self, payload: Dict[str, Any]) -> StepResult[MergeConflictObservation]:
        obs_data = payload.get("observation", payload)
        # reward and done live at the top level of payload, not inside observation
        reward = payload.get("reward", 0.0)
        done = payload.get("done", False)
        observation = MergeConflictObservation(
            file_content=obs_data.get("file_content", ""),
            filename=obs_data.get("filename", ""),
            conflict_count=obs_data.get("conflict_count", 0),
            task_id=obs_data.get("task_id", ""),
            branch_info=obs_data.get("branch_info", ""),
            conflicts_resolved=obs_data.get("conflicts_resolved", 0),
            total_conflicts=obs_data.get("total_conflicts", 0),
            feedback=obs_data.get("feedback", ""),
            done=done,
            reward=reward,
            last_action_error=obs_data.get("last_action_error"),
        )
        return StepResult(
            observation=observation,
            reward=reward,
            done=done,
        )

    def _parse_state(self, payload: Dict[str, Any]) -> MergeConflictState:
        return MergeConflictState(
            episode_id=payload.get("episode_id", ""),
            step_count=payload.get("step_count", 0),
            task_id=payload.get("task_id", "easy"),
            current_file_idx=payload.get("current_file_idx", 0),
            conflicts_resolved=payload.get("conflicts_resolved", 0),
            total_conflicts=payload.get("total_conflicts", 0),
            score=payload.get("score", 0.0),
            attempts=payload.get("attempts", 0),
            max_attempts=payload.get("max_attempts", 5),
        )

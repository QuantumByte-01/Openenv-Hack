"""Pydantic models for the Git Merge Conflict Resolution environment."""

from typing import Dict, List, Optional

from openenv.core.env_server import Action, Observation, State
from pydantic import Field


class MergeConflictAction(Action):
    """Action the agent takes to resolve a merge conflict."""

    resolved_content: str = Field(
        ..., description="The full resolved file content with all conflicts resolved"
    )


class MergeConflictObservation(Observation):
    """What the agent observes about the current merge conflict."""

    file_content: str = Field(
        default="", description="The file content with conflict markers (<<<<<<< ======= >>>>>>>)"
    )
    filename: str = Field(default="", description="Name of the conflicted file")
    conflict_count: int = Field(
        default=0, description="Number of conflict sections in the file"
    )
    task_id: str = Field(default="", description="Current task: easy, medium, hard, expert, or nightmare")
    branch_info: str = Field(
        default="",
        description="Context about what each branch was trying to do",
    )
    conflicts_resolved: int = Field(
        default=0, description="Number of conflicts resolved so far"
    )
    total_conflicts: int = Field(
        default=0, description="Total conflicts in this task"
    )
    feedback: str = Field(
        default="", description="Feedback from the last resolution attempt"
    )
    last_action_error: Optional[str] = Field(
        default=None, description="Error from the last action, if any"
    )


class MergeConflictState(State):
    """Internal state of the environment."""

    task_id: str = Field(default="easy")
    current_file_idx: int = Field(default=0)
    conflicts_resolved: int = Field(default=0)
    total_conflicts: int = Field(default=0)
    score: float = Field(default=0.0)
    attempts: int = Field(default=0)
    max_attempts: int = Field(default=5)

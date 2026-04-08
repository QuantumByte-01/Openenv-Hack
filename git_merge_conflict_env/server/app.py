"""FastAPI application for the Git Merge Conflict environment."""

from openenv.core.env_server import create_app

try:
    from ..models import MergeConflictAction, MergeConflictObservation
except ImportError:
    from git_merge_conflict_env.models import MergeConflictAction, MergeConflictObservation

from .environment import MergeConflictEnvironment

# Pass CLASS, not instance — OpenEnv creates instances per session
app = create_app(
    MergeConflictEnvironment,
    MergeConflictAction,
    MergeConflictObservation,
    env_name="git-merge-conflict-env",
)

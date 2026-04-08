"""Aspect-based grading for merge conflict resolutions.

Scoring uses five weighted aspects:
  - Conflict markers removed (0.15): no <<<<<<< ======= >>>>>>> remain
  - Key lines present     (0.35): critical lines from ground truth exist
  - Reject lines absent   (0.15): lines that should NOT be in output are absent
  - Text similarity        (0.25): difflib SequenceMatcher ratio
  - Syntax valid           (0.10): Python compile() succeeds (.py files)
"""

import difflib
import re
from dataclasses import dataclass
from typing import List, Optional


CONFLICT_MARKER_PATTERN = re.compile(r"^(<{7}|={7}|>{7})", re.MULTILINE)


@dataclass
class GradeResult:
    """Result of grading a single file resolution."""

    score: float  # 0.0 - 1.0
    conflicts_remaining: int
    feedback: str


def _normalize(text: str) -> List[str]:
    """Normalize text for comparison: strip trailing whitespace, remove blank line diffs."""
    lines = text.strip().splitlines()
    return [line.rstrip() for line in lines]


def _has_conflict_markers(text: str) -> bool:
    """Check if text still contains unresolved conflict markers."""
    return bool(CONFLICT_MARKER_PATTERN.search(text))


def _count_conflict_sections(text: str) -> int:
    """Count the number of <<<<<<< markers (one per conflict section)."""
    return len(re.findall(r"^<{7}", text, re.MULTILINE))


def _check_key_lines(agent_lines: List[str], key_lines: List[str]) -> float:
    """Return fraction of key_lines found as substrings in agent lines."""
    if not key_lines:
        return 1.0  # vacuously true
    found = 0
    for kl in key_lines:
        kl_stripped = kl.strip()
        if any(kl_stripped in line for line in agent_lines):
            found += 1
    return found / len(key_lines)


def _check_reject_lines(agent_lines: List[str], reject_lines: List[str]) -> float:
    """Return 1.0 if no reject_lines found, 0.0 if all found. Linear between."""
    if not reject_lines:
        return 1.0  # vacuously true
    found = 0
    for rl in reject_lines:
        rl_stripped = rl.strip()
        if any(rl_stripped in line for line in agent_lines):
            found += 1
    return 1.0 - (found / len(reject_lines))


def _check_syntax(text: str, filename: str) -> float:
    """Return 1.0 if Python syntax is valid, 0.0 otherwise. Non-.py files get 1.0."""
    if not filename.endswith(".py"):
        return 1.0
    try:
        compile(text, filename, "exec")
        return 1.0
    except SyntaxError:
        return 0.0


def _missing_key_lines(agent_lines: List[str], key_lines: List[str]) -> List[str]:
    """Return list of key_lines not found in agent resolution."""
    missing = []
    for kl in key_lines:
        kl_stripped = kl.strip()
        if not any(kl_stripped in line for line in agent_lines):
            missing.append(kl)
    return missing


def _present_reject_lines(agent_lines: List[str], reject_lines: List[str]) -> List[str]:
    """Return list of reject_lines found in agent resolution."""
    present = []
    for rl in reject_lines:
        rl_stripped = rl.strip()
        if any(rl_stripped in line for line in agent_lines):
            present.append(rl)
    return present


def grade_resolution(
    agent_resolution: str,
    ground_truth: str,
    original_conflict_count: int,
    key_lines: Optional[List[str]] = None,
    reject_lines: Optional[List[str]] = None,
    filename: str = "",
) -> GradeResult:
    """Grade an agent's conflict resolution against the ground truth.

    Uses five weighted aspects for scoring. Returns a GradeResult with
    score (0.0-1.0), remaining conflict count, and structured feedback.
    """
    key_lines = key_lines or []
    reject_lines = reject_lines or []

    # Empty / trivial resolution
    if not agent_resolution or len(agent_resolution.strip().splitlines()) < 2:
        return GradeResult(
            score=0.0,
            conflicts_remaining=original_conflict_count,
            feedback="Resolution is empty or too short.",
        )

    agent_lines = _normalize(agent_resolution)
    truth_lines = _normalize(ground_truth)

    # Exact match → perfect score
    if agent_lines == truth_lines:
        return GradeResult(
            score=1.0,
            conflicts_remaining=0,
            feedback="Perfect resolution! Exact match with expected output.",
        )

    # ── Compute aspect scores ─────────────────────────────
    markers_score = 0.0 if _has_conflict_markers(agent_resolution) else 1.0
    key_score = _check_key_lines(agent_lines, key_lines)
    reject_score = _check_reject_lines(agent_lines, reject_lines)
    similarity_score = difflib.SequenceMatcher(None, agent_lines, truth_lines).ratio()
    syntax_score = _check_syntax(agent_resolution, filename)

    # ── Weighted total ────────────────────────────────────
    score = (
        0.15 * markers_score
        + 0.35 * key_score
        + 0.15 * reject_score
        + 0.25 * similarity_score
        + 0.10 * syntax_score
    )

    # ── Build feedback ────────────────────────────────────
    remaining = _count_conflict_sections(agent_resolution)
    feedback_parts = []

    if markers_score < 1.0:
        feedback_parts.append(
            f"Conflict markers still present ({remaining} unresolved)."
        )

    if key_lines and key_score < 1.0:
        missing = _missing_key_lines(agent_lines, key_lines)
        feedback_parts.append(
            f"Missing {len(missing)}/{len(key_lines)} key elements."
        )

    if reject_lines and reject_score < 1.0:
        present = _present_reject_lines(agent_lines, reject_lines)
        feedback_parts.append(
            f"Contains {len(present)} incorrect element(s) that should not be present."
        )

    if similarity_score >= 0.9:
        feedback_parts.append(f"High similarity: {similarity_score:.0%}.")
    elif similarity_score >= 0.7:
        feedback_parts.append(f"Moderate similarity: {similarity_score:.0%}.")
    else:
        feedback_parts.append(f"Low similarity: {similarity_score:.0%}.")

    if syntax_score < 1.0:
        feedback_parts.append("Syntax errors detected in resolution.")

    return GradeResult(
        score=round(max(0.0, min(1.0, score)), 2),
        conflicts_remaining=remaining,
        feedback=" ".join(feedback_parts),
    )


def grade_multi_file(
    resolutions: List[str],
    ground_truths: List[str],
    conflict_counts: List[int],
    key_lines_list: Optional[List[List[str]]] = None,
    reject_lines_list: Optional[List[List[str]]] = None,
    filenames: Optional[List[str]] = None,
) -> GradeResult:
    """Grade a multi-file resolution (for hard/nightmare tasks).

    Scores each file independently, then averages.
    Adds a consistency bonus if all files are resolved correctly.
    """
    if len(resolutions) != len(ground_truths):
        return GradeResult(
            score=0.0,
            conflicts_remaining=sum(conflict_counts),
            feedback=f"Expected {len(ground_truths)} file resolutions, got {len(resolutions)}.",
        )

    n = len(resolutions)
    key_lines_list = key_lines_list or [[] for _ in range(n)]
    reject_lines_list = reject_lines_list or [[] for _ in range(n)]
    filenames = filenames or ["" for _ in range(n)]

    file_results = []
    for res, truth, count, kl, rl, fn in zip(
        resolutions, ground_truths, conflict_counts,
        key_lines_list, reject_lines_list, filenames,
    ):
        file_results.append(grade_resolution(res, truth, count, kl, rl, fn))

    avg_score = sum(r.score for r in file_results) / len(file_results)

    # Consistency bonus: if all files score >= 0.8, add 0.1
    all_good = all(r.score >= 0.8 for r in file_results)
    if all_good:
        avg_score = min(1.0, avg_score + 0.1)

    total_remaining = sum(r.conflicts_remaining for r in file_results)

    feedback_parts = []
    for i, r in enumerate(file_results):
        feedback_parts.append(f"File {i + 1}: {r.feedback}")
    if all_good:
        feedback_parts.append("Consistency bonus: +0.1 (all files resolved well).")

    return GradeResult(
        score=round(max(0.0, min(1.0, avg_score)), 2),
        conflicts_remaining=total_remaining,
        feedback=" | ".join(feedback_parts),
    )

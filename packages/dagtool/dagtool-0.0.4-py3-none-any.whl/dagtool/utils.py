from __future__ import annotations

import hashlib
from datetime import datetime
from typing import TypedDict

from airflow.models import Operator
from airflow.utils.task_group import TaskGroup
from pendulum import DateTime


class TaskMapped(TypedDict):
    """Task Mapped dict typed."""

    upstream: list[str]
    task: Operator | TaskGroup


def set_upstream(tasks: dict[str, TaskMapped]) -> None:
    """Set Upstream Task for each tasks in mapping.

    Args:
        tasks: A mapping of task_id and TaskMapped dict object.
    """
    for task in tasks:
        task_mapped: TaskMapped = tasks[task]
        if upstream := task_mapped["upstream"]:
            for t in upstream:
                try:
                    task_mapped["task"].set_upstream(tasks[t]["task"])
                except KeyError as e:
                    raise KeyError(
                        f"Task ids, {e}, does not found from the template."
                    ) from e


def change_tz(dt: DateTime | None, tz: str = "UTC") -> DateTime | None:
    if dt is None:
        return None
    return dt.in_timezone(tz)


def format_dt(
    dt: datetime | DateTime | None, fmt: str = "%Y-%m-%d %H:00:00%z"
) -> str | None:
    if dt is None:
        return None
    return dt.strftime(fmt)


def hash_sha256(data: str | bytes) -> str:
    """Calculates the SHA-256 hash of the given data.

    Args:
        data (str or bytes): The input data to be hashed.

    Returns:
        str: The hexadecimal representation of the SHA-256 hash.
    """
    if isinstance(data, str):
        data = data.encode("utf-8")  # Encode string to bytes

    sha256_hash = hashlib.sha256()
    sha256_hash.update(data)
    return sha256_hash.hexdigest()

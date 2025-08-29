"""Context management for test execution data."""

import time
from contextvars import ContextVar
from typing import Any

import pytest

from ._constants import ERROR_NO_CONTEXT
from ._models import DataRecord, SoftCheckRecord, StepRecord
from ._types import JsonData, TestContext

_ACTIVE_CONTEXT: ContextVar[TestContext | None] = ContextVar("_ACTIVE_CONTEXT", default=None)
STASH_CTX: pytest.StashKey[TestContext] = pytest.StashKey()
STASH_RESULTS: pytest.StashKey[list[dict[str, Any]]] = pytest.StashKey()


def get_context() -> TestContext:
    """Get the current test context.

    Returns:
        The current test context containing steps, soft checks, and data reports.

    Raises:
        RuntimeError: If called outside of a test context.
    """
    ctx = _ACTIVE_CONTEXT.get(None)
    if ctx is None:
        raise RuntimeError(ERROR_NO_CONTEXT)
    return ctx


def _get_next_sequence_number(ctx: TestContext) -> int:
    """Get the next sequence number for test records.

    Args:
        ctx: The test context to update.

    Returns:
        The next sequence number.
    """
    seq = ctx.get("seq", 0)
    ctx["seq"] = seq + 1
    return seq


def add_step_record(name: str) -> StepRecord:
    """Add a step record to the current test context.

    Args:
        name: The name of the step.

    Returns:
        The created step record.
    """
    ctx = get_context()
    seq = _get_next_sequence_number(ctx)
    record = StepRecord(name=name, seq=seq, start=time.monotonic(), time=time.monotonic())
    ctx["steps"].append(record)
    return record


def add_soft_check_record(message: str, passed: bool, details: str | list[str] | None = None) -> SoftCheckRecord:
    """Add a soft check record to the current test context.

    Args:
        message: The assertion message.
        passed: Whether the assertion passed.
        details: Optional details for the assertion.

    Returns:
        The created soft check record.
    """
    ctx = get_context()
    seq = _get_next_sequence_number(ctx)
    current_time = time.monotonic()
    record = SoftCheckRecord(message=message, passed=passed, details=details, seq=seq, time=current_time)
    ctx["soft_checks"].append(record)
    if not passed:
        ctx["soft_failures"].append(message)
    return record


def add_data_record(label: str, data: JsonData) -> DataRecord:
    """Add a data record to the current test context.

    Args:
        label: A descriptive label for the data.
        data: The data to attach.

    Returns:
        The created data record.
    """
    ctx = get_context()
    seq = _get_next_sequence_number(ctx)
    current_time = time.monotonic()
    record = DataRecord(label=label, seq=seq, time=current_time, payload=data)
    ctx["data_reports"].append(record)
    return record

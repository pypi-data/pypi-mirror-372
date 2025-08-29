"""Models for test records and data structures."""

import time
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from typing import Any, Protocol


class Serializable(Protocol):
    """Protocol for objects that can be serialized to dictionaries."""

    def to_dict(self) -> dict[str, Any]:
        """Convert the object to a dictionary representation."""
        ...


@dataclass
class BaseRecord(ABC):
    """Base class for all test records."""

    seq: int
    time: float

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """Convert the record to a dictionary representation."""


@dataclass
class StepRecord(BaseRecord):
    """Record for test steps with timing and error information."""

    name: str
    start: float
    end: float | None = None
    error: str | None = None

    def __post_init__(self) -> None:
        """Initialize the record after dataclass creation."""
        if not hasattr(self, "time"):
            self.time = self.start

    def finish(self, error: BaseException | None) -> None:
        """Mark the step as finished with optional error information.

        Args:
            error: Optional exception that occurred during step execution.
        """
        self.end = time.monotonic()
        if error is not None:
            self.error = repr(error)

    def to_dict(self) -> dict[str, Any]:
        """Convert the step record to a dictionary representation."""
        result = {
            "name": self.name,
            "start": self.start,
            "end": self.end if self.end is not None else self.start,
            "seq": self.seq,
        }
        if self.error:
            result["error"] = self.error
        return result

    @property
    def duration(self) -> float:
        """Calculate the duration of the step in seconds."""
        if self.end is None:
            return 0.0
        return self.end - self.start


@dataclass
class SoftCheckRecord(BaseRecord):
    """Record for soft assertion checks."""

    message: str
    passed: bool
    details: str | list[str] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert the soft check record to a dictionary representation."""
        return asdict(self)


@dataclass
class DataRecord(BaseRecord):
    """Record for data attachments."""

    label: str
    payload: Any

    def to_dict(self) -> dict[str, Any]:
        """Convert the data record to a dictionary representation."""
        return {
            "label": self.label,
            "seq": self.seq,
            "time": self.time,
            "payload": self.payload,
        }

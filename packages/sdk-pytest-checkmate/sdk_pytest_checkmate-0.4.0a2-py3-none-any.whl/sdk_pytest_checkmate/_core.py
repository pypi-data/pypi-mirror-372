"""Core functionality for test steps, soft assertions, and data attachments."""

import ast
import inspect
import re
import time
from pathlib import Path
from types import TracebackType
from typing import Self

from ._context import add_data_record, add_soft_check_record, add_step_record
from ._models import DataRecord, StepRecord
from ._types import JsonData


class StepContext:
    """Context manager for recording test steps with timing information.

    This class provides both synchronous and asynchronous context manager
    protocols for recording test steps.
    """

    def __init__(self, name: str) -> None:
        """Initialize the step context.

        Args:
            name: The name of the step to be recorded.
        """
        self.name = name
        self._record: StepRecord | None = None

    def __enter__(self) -> Self:
        """Enter the synchronous context manager."""
        self._record = add_step_record(self.name)
        if self._record is not None:
            self._record.start = time.monotonic()
            self._record.end = None
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool:
        """Exit the synchronous context manager.

        Args:
            exc_type: Exception type if an exception occurred.
            exc_value: Exception instance if an exception occurred.
            traceback: Traceback object if an exception occurred.

        Returns:
            False to propagate any exception that occurred.
        """
        if self._record is not None:
            self._record.finish(exc_value)
        return False

    async def __aenter__(self) -> Self:
        """Enter the asynchronous context manager."""
        return self.__enter__()

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool:
        """Exit the asynchronous context manager.

        Args:
            exc_type: Exception type if an exception occurred.
            exc_value: Exception instance if an exception occurred.
            traceback: Traceback object if an exception occurred.

        Returns:
            False to propagate any exception that occurred.
        """
        return self.__exit__(exc_type, exc_value, traceback)


def step(name: str) -> StepContext:
    """Create a step context manager for recording test steps.

    Args:
        name: The name of the step to be recorded.

    Returns:
        A step context manager that can be used with 'with' statement.

    Example:
        >>> with step("Login user"):
        ...     # Step implementation
        ...     pass

        >>> async with step("Fetch data"):
        ...     # Async step implementation
        ...     pass
    """
    return StepContext(name)


def soft_assert(condition: bool, message: str | None = None, details: str | list[str] | None = None) -> bool:
    """Record a non-fatal assertion that doesn't immediately fail the test.

    Soft assertions allow tests to continue execution even when some
    assertions fail, collecting all failures for reporting at the end.

    Args:
        condition: The boolean condition to check.
        message: Optional descriptive message for the assertion.
                Defaults to "Soft assertion" if not provided.
        details: Optional details for the assertion. If not provided,
                the condition will be analyzed and shown with actual values.
                Can be a string or list of strings.

    Returns:
        The boolean value of the condition.

    Example:
        >>> soft_assert(user.name is not None, "User should have a name")
        >>> soft_assert(user.email.endswith("@company.com"), "Email should be company domain",
        ...            details="Checking domain validation rules")
        >>> soft_assert(len(items) > 0, "Items list should not be empty",
        ...            details=["List length check", "Validation step 1"])
    """
    msg = message or "Soft assertion"

    if details is None:
        try:
            frame = inspect.currentframe().f_back  # type: ignore
            code = frame.f_code  # type: ignore
            filename = code.co_filename
            lineno = frame.f_lineno  # type: ignore
            glb, loc = frame.f_globals, frame.f_locals  # type: ignore

            lines = Path(filename).read_text(encoding="utf-8").splitlines()
            if not (0 <= lineno - 1 < len(lines)):
                raise OSError

            start = lineno - 1
            call_name_re = re.compile(r"(\b|\.)soft_assert\s*\(")
            while start >= 0 and not call_name_re.search(lines[start]):
                start -= 1
            if start < 0:
                raise RuntimeError

            call_text = lines[start].strip()
            i = start + 1
            paren = call_text.count("(") - call_text.count(")")
            while paren > 0 and i < len(lines):
                call_text += " " + lines[i].strip()
                paren += lines[i].count("(") - lines[i].count(")")
                i += 1

            m = call_name_re.search(call_text)
            if not m:
                raise RuntimeError
            pos = call_text.find("(", m.end() - 1)
            if pos == -1:
                raise RuntimeError

            depth = 1
            j = pos + 1
            while j < len(call_text) and depth > 0:
                c = call_text[j]
                if c == "(":
                    depth += 1
                elif c == ")":
                    depth -= 1
                j += 1
            args_content = call_text[pos + 1 : j - 1].strip()

            condition_str = None
            args_ast = ast.parse(f"f({args_content})", mode="eval")
            if isinstance(args_ast.body, ast.Call):
                call = args_ast.body
                if call.args:
                    condition_str = ast.unparse(call.args[0])
                else:
                    for kw in call.keywords or []:
                        if kw.arg == "condition":
                            condition_str = ast.unparse(kw.value)
                            break

            if condition_str:
                try:
                    tree = ast.parse(condition_str, mode="eval")
                    if isinstance(tree.body, ast.Compare) and tree.body.ops and tree.body.comparators:
                        nodes = [tree.body.left] + list(tree.body.comparators)  # noqa: RUF005
                        vals = []
                        for n in nodes:
                            src = ast.unparse(n)
                            try:
                                v = eval(src, glb, loc)  # noqa: S307
                                vals.append(repr(v))
                            except Exception:
                                vals.append(src)
                        op_map = {
                            ast.Gt: ">",
                            ast.Lt: "<",
                            ast.GtE: ">=",
                            ast.LtE: "<=",
                            ast.Eq: "==",
                            ast.NotEq: "!=",
                            ast.Is: "is",
                            ast.IsNot: "is not",
                            ast.In: "in",
                            ast.NotIn: "not in",
                        }
                        ops = [op_map.get(type(op), ast.unparse(op)) for op in tree.body.ops]
                        evaluated = " ".join(v for pair in zip(vals, ops + [""], strict=False) for v in pair if v)  # noqa: RUF005
                        details = f"{condition_str} => ({evaluated})"
                    else:
                        try:
                            result_val = eval(condition_str, glb, loc)  # noqa: S307
                            details = f"{condition_str} => (evaluates to {result_val!r})"
                        except Exception:
                            details = condition_str
                except Exception:
                    details = condition_str
            else:
                details = str(bool(condition))
        except Exception:
            details = str(bool(condition))

    add_soft_check_record(msg, bool(condition), details)
    return bool(condition)


def add_data_report(data: JsonData, label: str) -> DataRecord:
    """Attach arbitrary data to the test timeline for inspection in reports.

    Args:
        data: The data to attach. Can be any JSON-serializable object.
        label: A descriptive label for the data that appears in reports.

    Returns:
        The created data record.

    Example:
        >>> config = {"endpoint": "/api/users", "timeout": 30}
        >>> add_data_report(config, "API Configuration")

        >>> response_data = {"status": 200, "body": {"id": 123}}
        >>> add_data_report(response_data, "API Response")
    """
    return add_data_record(label, data)

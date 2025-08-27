#!/usr/bin/env python3
# pyvider/hcl/exceptions.py

from attrs import define, field


class HclError(Exception):
    """Base class for errors related to HCL processing in Pyvider."""

    pass


@define(frozen=True, slots=True, auto_exc=True)
class HclParsingError(HclError):
    """
    Raised when HCL parsing or schema validation fails.

    This is an attrs-based exception class for structured error reporting.
    """

    message: str = field()
    source_file: str | None = field(default=None)
    line: int | None = field(default=None)
    column: int | None = field(default=None)

    def __str__(self) -> str:
        """Provides a detailed error message including source location if available."""
        if self.source_file and self.line is not None and self.column is not None:
            return f"{self.message} (at {self.source_file}, line {self.line}, column {self.column})"
        elif self.source_file and self.line is not None:
            return f"{self.message} (at {self.source_file}, line {self.line})"
        elif self.source_file:
            return f"{self.message} (at {self.source_file})"
        return self.message

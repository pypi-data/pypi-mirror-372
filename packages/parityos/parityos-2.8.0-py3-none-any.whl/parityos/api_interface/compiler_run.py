"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2020-2024.
All rights reserved.

Tools to process the results from the ParityOS cloud service.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Union

from parityos.base import JSONMappingType


DateStr = Union[datetime, str]  # type: TypeAlias


class CompilerRunStatus(Enum):
    """
    Enum for compiler run status.
    """

    SUBMITTED = "S"
    RUNNING = "R"
    COMPLETED = "C"
    FAILED = "F"


@dataclass
class CompilerRun:
    """
    Encapsulates a compiler run; has attributes which describe relevant times
    at which they were submitted, started, and eventually finished or failed
    (in which case, a reason for failure is also given).

    :param id: The UUID4 id of the compiler run in ParityOS cloud database.
    :param submission_id: The UUID4 id of the submission which triggered compile run.
    :param status: The status of the submission; see the `CompilerRunStatus` enum.
    :param submitted_at: Time at which the run was queued for execution, as `datetime` object.
    :param started_at: Time at which the run started being executed, as `datetime` object.
    :param finished_at: Time at which the run was completed, as `datetime` object.
    :param failed_at: time at which run failed
    :param failure_reason: reason for which run failed
    """

    id: str
    submission_id: str
    status: Union[CompilerRunStatus, str]
    submitted_at: Optional[DateStr] = None
    started_at: Optional[DateStr] = None
    finished_at: Optional[DateStr] = None
    failed_at: Optional[DateStr] = None
    failure_reason: Optional[str] = ""

    def __post_init__(self):
        """Convert attributes to their intended type if they were provided as strings."""
        # Map the status to the corresponding Enum instance.
        self.status = CompilerRunStatus(self.status)
        # Map date times in string format to datetime instances
        self.submitted_at = _str_to_datetime(self.submitted_at)
        self.started_at = _str_to_datetime(self.started_at)
        self.finished_at = _str_to_datetime(self.finished_at)
        self.failed_at = _str_to_datetime(self.failed_at)

    @classmethod
    def from_json(cls, data: JSONMappingType) -> "Self":
        """
        Creates a CompilerRun object from a JSON-like data dictionary.
        :return: a CompilerRun object
        """
        return cls(**data)

    def __str__(self) -> str:
        """
        Return useful information about the compiler run in string format.
        """
        info_lines = [f"Compiler run {self.id}. ", f"Status: {self.status}"]
        if self.submitted_at:
            info_lines.append(f"The compiler run was submitted at {self.submitted_at.ctime()}.")

        if self.started_at:
            info_lines.append(f"The compilation started at {self.started_at.ctime()}.")
            if self.finished_at:
                duration_in_seconds = (self.finished_at - self.started_at).total_seconds()
                info_lines.append(f"The compilation took {duration_in_seconds:0.2f} seconds.")

        if self.failed_at:
            if self.started_at:
                duration_in_seconds = (self.failed_at - self.started_at).total_seconds()
                info_lines.append(
                    f"The compilation was aborted after {duration_in_seconds:0.2f} seconds."
                )
            else:
                info_lines.append(f"An error occurred at {self.failed_at.ctime()}.")

        if self.failure_reason:
            info_lines.append(self.failure_reason)

        return "\n".join(info_lines)


def _str_to_datetime(date: Union[datetime, str]) -> datetime:
    """Helper method to convert dates in string format to datetime instances."""
    return (
        datetime.fromisoformat(date.replace("Z", "+00:00"))
        if date and isinstance(date, str)
        else date
    )

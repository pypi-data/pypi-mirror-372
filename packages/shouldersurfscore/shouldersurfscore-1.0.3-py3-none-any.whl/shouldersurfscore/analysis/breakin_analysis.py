import datetime
from dataclasses import asdict, dataclass, fields
from typing import Any

import dacite
from noiftimer import Timer
from typing_extensions import Self

# type alias
BreakInDict = dict[str, str | int | float | datetime.timedelta | bool]


@dataclass(frozen=True)
class BreakInAnalysis:
    """
    Dataclass representing the results of a break-in attempt.
    """

    actual_password: str
    observed_password: str
    # The index of the actual password in the list of guesses.
    # -1 if not present
    password_index: int | None
    # The ratio of the actual password index to length of guess list.
    password_index_percent: float | None
    # The total time accrued by timeouts during breakin attempt.
    elapsed_time: datetime.timedelta
    # Whether the attack was successful.
    device_unlocked: bool

    def __str__(self) -> str:
        text: str = "Break-In Analysis\n"
        text += "-" * len(text) + "\n"
        for field in fields(self):
            text += f"{field.name}: "
            val: Any = getattr(self, field.name)
            if isinstance(val, datetime.timedelta):
                text += (
                    "0s"
                    if val.total_seconds() == 0
                    else Timer.format_time(val.total_seconds(), True)
                )
            else:
                text += str(val)
            text += "\n"
        return text.strip("\n")

    def asdict(self) -> BreakInDict:
        """
        Convert this instance into a dictionary.

        Returns
        -------
        BreakInDict
            This instance as a dictionary.
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, data: BreakInDict) -> Self:
        """
        Create an instance from a dictionary.

        Parameters
        ----------
        data : BreakInDict
            The dictionary to populate the instance with.

        Returns
        -------
        BreakInAnalysis
            The populated dataclass instance.
        """
        return dacite.from_dict(cls, data)

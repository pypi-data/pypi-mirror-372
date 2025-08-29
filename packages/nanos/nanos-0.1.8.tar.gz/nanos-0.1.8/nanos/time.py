from __future__ import annotations

import datetime
import math
import time
import typing as t

DEFAULT_TIMER_PRECISION: t.Final = 2


class Timer:
    """
    Initializes a Timer instance with optional precision.

    Args:
        precision (int): The number of decimal places to use
            for displaying fractional seconds. Defaults to 2.
    """

    def __init__(self, precision: int = DEFAULT_TIMER_PRECISION) -> None:
        self.precision = precision
        self.start: float | None = None
        self.end: float | None = None

    def __enter__(self) -> Timer:
        self.start = time.time()
        return self

    def __exit__(self, *args: t.Any) -> None:
        self.end = time.time()

    def __str__(self) -> str:
        return self.verbose()

    def __repr__(self) -> str:
        return f"<Timer [start={self.start}, end={self.end}]>"

    def verbose(self) -> str:
        """
        Returns a formatted string representing the elapsed time with a precision
        specified by the Timer instance.

        The elapsed time is formatted as a string in the format of 'H:MM:SS.F',
        where 'H:MM:SS' is the hours, minutes, and seconds, and 'F' is the
        fractional seconds with a number of decimal places equal to the precision.

        Returns:
            str: The formatted elapsed time as a string.
        """
        fraction_seconds, whole_seconds = math.modf(self.elapsed)
        rounded_fraction = round(fraction_seconds, self.precision)
        if rounded_fraction >= 1:
            whole_seconds += 1
            formatted_fraction = "0" * self.precision
        elif fraction_seconds == 0:
            formatted_fraction = "0" * self.precision
        else:
            fraction = int(rounded_fraction * 10**self.precision)
            formatted_fraction = str(fraction).zfill(self.precision)
        return f"{datetime.timedelta(seconds=whole_seconds)}.{formatted_fraction}"

    @property
    def elapsed(self) -> float:
        """
        Calculates the elapsed time in seconds.

        This property computes the difference between the end time and the
        start time of the Timer. If the Timer has not been started, it returns
        0.0. If the Timer is running (i.e., the end time is not set), it uses
        the current time as the end time.

        Returns:
            float: The elapsed time in seconds.
        """
        if not self.start:
            return 0.0
        return (self.end or time.time()) - self.start

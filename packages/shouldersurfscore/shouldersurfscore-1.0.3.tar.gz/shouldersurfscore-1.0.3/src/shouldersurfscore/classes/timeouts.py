import abc
import datetime
from collections.abc import Sequence

from typing_extensions import override


def delta_from_seconds(seconds: float) -> datetime.timedelta:
    """
    Convenience function for returning a timedelta from a seconds value.

    Parameters
    ----------
    seconds : float
        The number of seconds.

    Returns
    -------
    datetime.timedelta
        A corresponding timedelta.
    """
    return datetime.timedelta(seconds=seconds)


class Timeout(abc.ABC):
    """
    Interface for simulating a timeout mechanism that returns
    a sequence of timeout values.

    The sequence can be delivered by either calling the object's `wait` method
    or by passing the instance to the builtin `next` function.
    >>> t = ConstantTimeout(timedelta(seconds=1))
    >>> total = timedelta()
    >>> for _ in range(10):
    >>>   total += t.wait()
    >>> total.total_seconds()
    10

    OR

    >>> for _ in range(10):
    >>>   total += next(t)
    >>> total.total_seconds()
    10

    Implementers must implement the following methods:

    `def wait(self) -> datetime.timedelta`

    `def reset(self) -> None`

    The `wait` method should return a `datetime.timedelta` object
    representing the length of the timeout.

    It should also prime the instance to deliver
    the next desired timeout when `wait` is called again.

    The `reset` function should reset any internal state needed by the implementation.

    See the below implemented classes for examples.
    """

    def __next__(self) -> datetime.timedelta:
        return self.wait()

    def _timedelta_is_invalid(self, delta: datetime.timedelta) -> bool:
        """
        Check if a timedelta is invalid.

        Parameters
        ----------
        delta : datetime.timedelta
            The timedelta to check.

        Returns
        -------
        bool
            Whether the timedelta is invalid or not.
        """
        return delta.total_seconds() < 0

    @abc.abstractmethod
    def wait(self) -> datetime.timedelta:
        """
        Returns the time to be waited.

        Returns
        -------
        datetime.timedelta
            The amound of time to wait.
        """

    @abc.abstractmethod
    def reset(self) -> None:
        """
        Reset the internal state of this timeout.
        """


class ConstantTimeout(Timeout):
    """
    Implements a constant timeout.
    """

    def __init__(
        self, length: datetime.timedelta = datetime.timedelta(seconds=0)
    ) -> None:
        """
        Initialize the instance with the length of the timeout.

        Parameters
        ----------
        length : datetime.timedelta, optional
            The length of the timeout, by default datetime.timedelta(seconds=0).

        Raises
        ------
        ValueError
            If `length` has a negative value.
        """
        if self._timedelta_is_invalid(length):
            raise ValueError("Timeout length must be 0 or greater.")
        self._length: datetime.timedelta = length

    @override
    def wait(self) -> datetime.timedelta:
        return self._length

    @override
    def reset(self) -> None:
        pass


class LinearTimeout(Timeout):
    """
    Implements a linear timeout sequence.

    Each subsequent value will be longer be some supplied increment.

    >>> t = LinearTimeout(timedelta(seconds=1))
    >>> next(t)
    0
    >>> next(t)
    1
    >>> next(t)
    2
    >>> next(t)
    3
    """

    def __init__(
        self,
        increment: datetime.timedelta,
        initial_wait: datetime.timedelta = datetime.timedelta(seconds=0),
    ) -> None:
        """
        Initialize the instance with an increment and initial timeout value.

        Parameters
        ----------
        increment : datetime.timedelta
            The amount of time to be cumulatively added to the timeout.
        initial_wait : datetime.timedelta, optional
            The initial amount of time to wait, by default datetime.timedelta(seconds=0).

        Raises
        ------
        ValueError
            If either `increment` or `initial_wait` are negative.
        """
        if self._timedelta_is_invalid(increment):
            raise ValueError("Timeout increment must be 0 or greater.")
        if self._timedelta_is_invalid(initial_wait):
            raise ValueError("Initial timeout must be 0 or greater.")
        self._increment: datetime.timedelta = increment
        self._initial_wait: datetime.timedelta = initial_wait
        self._current_wait: datetime.timedelta = initial_wait

    @override
    def wait(self) -> datetime.timedelta:
        amount: datetime.timedelta = self._current_wait
        self._current_wait += self._increment
        return amount

    @override
    def reset(self) -> None:
        self._current_wait = self._initial_wait


class ArbitraryTimeout(Timeout):
    """
    Implements an arbitrary timeout sequence.

    If `wait` is called more times than the length of the given timeout sequence,
    the last timout in the sequence will be returned each time until `reset` is called.
    """

    def __init__(self, deltas: Sequence[datetime.timedelta]) -> None:
        """
        Initialize the instance with a sequence of timedeltas.

        Parameters
        ----------
        deltas : Sequence[datetime.timedelta]
            The list of timedeltas.

        Raises
        ------
        ValueError
            If `deltas` is an empty sequence or any timedelta in
            the sequence is negative.
        """
        if not deltas:
            raise ValueError("`deltas` cannot be empty.")
        for delta in deltas:
            if self._timedelta_is_invalid(delta):
                raise ValueError("No timedelta can be negative.")
        self._deltas: Sequence[datetime.timedelta] = deltas
        self._length: int = len(deltas)
        self._i: int = 0

    @override
    def wait(self) -> datetime.timedelta:
        if self._i >= self._length:
            return self._deltas[-1]
        delta: datetime.timedelta = self._deltas[self._i]
        self._i += 1
        return delta

    @override
    def reset(self) -> None:
        self._i = 0

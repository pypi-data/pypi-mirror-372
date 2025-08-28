import datetime
import enum

from shouldersurfscore.classes.timeouts import ConstantTimeout, Timeout


class Gate(enum.Enum):
    """
    Enum representing the various states of a `GateKeeper`.

    `UNLOCKED`: The correct password has been entered
    and whatever the gate is guarding can be
    freely accessed by the user.

    `LOCKED`: The correct password has not been entered,
    but the maximum allowed attempts has not been depleted.

    `LOCKED_OUT`: There are no more password attempts remaining
    until the gatekeeper is reset.
    """

    UNLOCKED = 0
    LOCKED = 1
    LOCKED_OUT = 2


class GateError(Exception):
    """Base exception for `Gate` related errors."""


class UnlockedError(GateError):
    """
    Type of exception to raise when a prohibited action
    is attempted when the gatekeeper is unlocked
    such as trying to unlock an already unlocked gatekeeper.
    """


class LockedError(GateError):
    """
    Type of exception to raise when a prohibited action
    is attempted when the gatekeeper is locked
    such as trying to set a password.
    """


class LockedOutError(GateError):
    """
    Type of exception to raise when a prohibited action
    is attempted when the gatekeeper is locked out
    such as trying to unlock the gatekeeper.
    """


class GateKeeper:
    """
    A class that guards access to a resource.

    An instance has one of three `Gate` states at any given time:<br>
    `UNLOCKED`, `LOCKED`, and `LOCKED_OUT`

    Typically a gate is unlocked with a password,
    but it can be used without one by setting it to `None`.<br>
    It can then be unlocked by passing `None` to the `unlock()` function.

    A gatekeeper can have an optional max attempts property.<br>
    When that many calls to `unlock()` with incorrect passwords are made,
    the gatekeeper will be put into the `LOCKED_OUT` state.<br>
    Trying to call `unlock()` on a locked out gatekeeper will raise a `LockedOutError`.<br>
    `reset()` can be called to reset the attempts made to 0 and lock the gate.

    A gatekeeper can also have an optional timeout simulation mechanism.<br>
    Whenever an incorrect password is passed to the `unlock()` function,
    the simulated amount of time spent waiting to reattempt unlocking the gate
    will be accumulated in the `elapsed_time` property.<br>
    If a `timeout` instance is not provided, this property will always return a 0s `timedelta`.<br>
    When `reset()` is called, this accumulator is also reset.

    Public `GateKeeper` properties can only be modified when the gate is unlocked.<br>
    Attempting to change them when the gate is locked or locked out will raise an exception.
    """

    def __init__(
        self,
        password: str | None = None,
        max_attempts: int | None = None,
        timeout: Timeout | None = None,
    ) -> None:
        """
        Initialize a gatekeeper.<br>
        After initialization, this gate will be in the `LOCKED` state.

        Parameters
        ----------
        password : str | None, optional
            The initial password for the gatekeeper, by default None.
        max_attempts : int | None, optional
            The maximum unlocking attempts that can be made before being a `LOCKED_OUT` state,
            by default None.
        timeout : Timeout | None, optional
            A `Timeout` class to simulate time spent waiting after incorrect password attempts,
            by default None.
        """
        # Will get set to `LOCKED` at the end of initialization
        self._gate: Gate = Gate.UNLOCKED
        self._password: str | None
        self.set_password(password)
        self._max_attempts: int | None
        self.max_attempts = max_attempts
        self._attempts_made: int = 0
        self._timeout: Timeout
        self.set_timeout(timeout)
        self._elapsed_time: datetime.timedelta = datetime.timedelta()
        self.lock()

    def force_unlock(self) -> None:
        """
        Force the gate to be unlocked without entering a password.<br>
        Does not reset any properties or components.
        """
        self._gate = Gate.UNLOCKED

    def lock(self) -> None:
        """
        Lock the gate.

        The number of attempts made to unlock the gate,
        the accumulated timeout, and timeout mechanism will all be reset.

        Raises
        ------
        LockedError
            If the gate is already locked.
        """
        if not self.is_unlocked:
            raise LockedError("The gate is already locked.")
        self._gate = Gate.LOCKED
        self._timeout.reset()
        self._attempts_made = 0
        self._elapsed_time = datetime.timedelta(0)

    def reset(self) -> None:
        """
        Resets the gatekeeper to its initial state and locks the gate.
        """
        self._gate = Gate.UNLOCKED
        self.lock()

    def set_password(self, password: str | None) -> None:
        """
        Set the password.

        Parameters
        ----------
        password : str | None
            The new password.

        Raises
        ------
        LockedError
            When this is called with the gate in a state other than `UNLOCKED`.
        """
        if not self.is_unlocked:
            raise LockedError("A password can only be set when the gate is unlocked.")
        self._password = password

    def set_timeout(self, timeout: Timeout | None) -> None:
        """
        Set (or remove) the timeout mechanism.

        Parameters
        ----------
        timeout : Timeout | None
            The new timeout object.<br>
            If `None` there will be no timeout accumulated after incorrect
            unlock attempts.

        Raises
        ------
        LockedError
            When this is called with the gatekeeper in a state other than `UNLOCKED`.
        """
        if not self.is_unlocked:
            raise LockedError(
                "Timeout can only be set when the gatekeeper is unlocked."
            )
        # default to a constant timeout of 0s
        self._timeout = timeout if timeout else ConstantTimeout()

    def unlock(self, password: str | None) -> bool:
        """
        Attempt to unlock the gate with the supplied password.<br>
        If an incorrect password is supplied, the attempts remaining before lockout
        will decrement by 1 and any simulated timeout will be accumulated.<br>
        If this attempt would put the gatekeeper into lockout, no timeout will be accumulated.

        Parameters
        ----------
        password : str | None
            The password to use.

        Returns
        -------
        bool
            Whether the gate was unlocked.

        Raises
        ------
        UnlockedError
            When this is called while the gate is already unlocked.
        LockedOutError
            When this is called while the gatekeeper is locked out.
        """
        if self.is_unlocked:
            raise UnlockedError("The gatekeeper is already unlocked.")
        if self.is_locked_out:
            raise LockedOutError("Can't unlock a locked out gatekeeper.")
        self._attempts_made += 1
        if password == self._password:
            self._gate = Gate.UNLOCKED
            return True
        # No timeout accumulated if gatekeeper will be locked out by attempt
        if self.attempts_remaining == 0:
            self._gate = Gate.LOCKED_OUT
        else:
            self._elapsed_time += next(self._timeout)
        return False

    @property
    def max_attempts(self) -> int | None:
        """
        The number of unlock attempts that can be made before lockout.<br>
        If `None`, then the gatekeeper will never go into lockout.
        """
        return self._max_attempts

    @max_attempts.setter
    def max_attempts(self, num: int | None) -> None:
        """
        Set or remove the number of max attempts.

        Parameters
        ----------
        num : int | None
            The new number of max attempts.<br>
            If `None`, infinite unlock attempts can be made.

        Raises
        ------
        LockedError
            If this property is set while the gate is not unlocked.
        ValueError
            If `num` is less than 1.
        """
        if not self.is_unlocked:
            raise LockedError(
                "Can't change max attempts when the gatekeeper is locked."
            )
        if num is not None and num < 1:
            raise ValueError("Number of max attempts must be `None` or greater than 0.")
        self._max_attempts = num

    @property
    def attempts_made(self) -> int:
        """The number of unlock attempts that have been made since the gate was last locked."""
        return self._attempts_made

    @property
    def attempts_remaining(self) -> int | None:
        """
        The number of attempts remaining before lockout.

        Returns
        -------
        int | None
            The number of attempts remaining.<br>
            If `max_attempts` is `None`, this will return `None`.
        """
        return (
            self.max_attempts
            if not self.max_attempts
            else self.max_attempts - self.attempts_made
        )

    @property
    def elapsed_time(self) -> datetime.timedelta:
        """The total time accumulated from timeouts since the last time the gate was locked."""
        return self._elapsed_time

    @property
    def status(self) -> Gate:
        """
        The current state of the gate.<br>
        Can either be `UNLOCKED`, `LOCKED`, or `LOCKED_OUT`.
        """
        return self._gate

    @property
    def is_unlocked(self) -> bool:
        """Whether the gate is unlocked."""
        return self.status == Gate.UNLOCKED

    @property
    def is_locked(self) -> bool:
        """Whether the gate is locked."""
        return self.status == Gate.LOCKED

    @property
    def is_locked_out(self) -> bool:
        """Whether the gate is locked out."""
        return self.status == Gate.LOCKED_OUT

import datetime
from dataclasses import dataclass

from typing_extensions import Self

from shouldersurfscore.classes.gatekeeper import Gate, GateKeeper
from shouldersurfscore.classes.keyboard import Keyboard
from shouldersurfscore.classes.password_rules import (
    PasswordRule,
    ValidCharactersPasswordRule,
)
from shouldersurfscore.classes.password_validator import PasswordValidator
from shouldersurfscore.classes.timeouts import Timeout


class TypeableCharactersPasswordRule(ValidCharactersPasswordRule):
    """Subclasses `ValidCharactersPasswordRule` to differentiate
    the rule from ones enforcing an arbitrary list of valid characters."""


# This is to prevent direct access to the gatekeeper of a device
# without needing a forwarding method for each of these attributes
@dataclass
class GateKeeperData:
    """
    Data object representing the state of a `GateKeeper` instance.
    """

    status: Gate
    max_attempts: int | None
    attempts_made: int
    attempts_remaining: int | None
    elapsed_time: datetime.timedelta


class InvalidPasswordError(Exception):
    """Exception class for trying to set invalid passwords."""

    @classmethod
    def from_password(cls: type[Self], password: str) -> Self:
        """
        Create an instance with a formatted error message.

        Parameters
        ----------
        password : str
            The invalid password to use in the exception message.

        Returns
        -------
        InvalidPasswordError
            The exception instance to raise.
        """
        return cls(f"'{password}' is not a valid password.")


class Device:
    """
    Class representing a device than can be unlocked/locked.

    Intended to be constructed using the `DeviceBuilder` class rather than instantiated directly.
    """

    def __init__(
        self,
        keyboard: Keyboard | None = None,
        gatekeeper: GateKeeper | None = None,
        password_validator: PasswordValidator | None = None,
    ) -> None:
        """
        Initialize a device.

        The intended way to create devices is with the `DeviceBuilder` class
        rather than here directly.

        Parameters
        ----------
        keyboard : Keyboard | None, optional
            The keyboard for this device, defaults to an empty `Keyboard` instance.
        gatekeeper : GateKeeper | None, optional
            The gatekeeper for this device, by default None.<br>
            If not given, a gatekeeper with no password, no max unlock attempts, and no timeout will be used.
        password_validator : PasswordValidator | None, optional
            The password validator for this device, by default None.<br>
            If not provided, any password will be valid.
        """
        self._keyboard: Keyboard = keyboard if keyboard else Keyboard()
        self._gatekeeper: GateKeeper = gatekeeper if gatekeeper else GateKeeper()
        self._password_validator: PasswordValidator = (
            password_validator if password_validator else PasswordValidator([])
        )

    @property
    def keyboard(self) -> Keyboard:
        """The keyboard for this device."""
        return self._keyboard

    @property
    def gatekeeper(self) -> GateKeeperData:
        """The current status of this device's gatekeeper."""
        return GateKeeperData(
            self._gatekeeper.status,
            self._gatekeeper.max_attempts,
            self._gatekeeper.attempts_made,
            self._gatekeeper.attempts_remaining,
            self._gatekeeper.elapsed_time,
        )

    @property
    def is_unlocked(self) -> bool:
        """Whether the device is unlocked."""
        return self._gatekeeper.is_unlocked

    @property
    def is_locked(self) -> bool:
        """Whether the device is locked."""
        return self._gatekeeper.is_locked

    @property
    def is_locked_out(self) -> bool:
        """Whether the device is locked out."""
        return self._gatekeeper.is_locked_out

    @property
    def password_validator(self) -> PasswordValidator:
        """The password validator used by this device."""
        return self._password_validator

    def is_valid_password(self, password: str) -> bool:
        """
        Check if a password could be used as the device password.

        Parameters
        ----------
        password : str
            The password to test.

        Returns
        -------
        bool
            Whether `password` satisfies the device's password rules.
        """
        return self._password_validator.is_valid(password)

    def is_invalid_password(self, password: str) -> bool:
        """
        Check if a password could not be used as the device password.

        Parameters
        ----------
        password : str
            The password to test.

        Returns
        -------
        bool
            Whether `password` violates the device's password rules.
        """
        return self._password_validator.is_invalid(password)

    def set_password(self, password: str | None) -> None:
        """
        Set a new password for this device.

        Parameters
        ----------
        password : str | None
            The new password.<br>
            If `None`, the device can be unlocked with `unlock(None)`.

        Raises
        ------
        InvalidPasswordError
            If `password` is not `None` and isn't valid according to the device's password rules.
        LockedError
            If this function is called when the device is not unlocked.
        """
        if password is not None and self._password_validator.is_invalid(password):
            raise InvalidPasswordError.from_password(password)
        self._gatekeeper.set_password(password)

    def unlock(self, password: str | None) -> bool:
        """
        Attempt to unlock this device with a password.

        Parameters
        ----------
        password : str | None
            The password to enter.

        Returns
        -------
        bool
            Whether the unlock attempt was successful.

        Raises
        ------
        UnlockedError
            If the device is already unlocked.
        LockedOutError
            If the device is in lockout.
        """
        return self._gatekeeper.unlock(password)

    def lock(self) -> None:
        """
        Lock this device and reset gatekeeper metrics.
        """
        if self.is_unlocked:
            self._gatekeeper.lock()

    def reset(self) -> None:
        """
        Reset this device's gatekeeper and lock it.<br>
        This will reset the data available through the `gatekeeper` property.
        """
        self._gatekeeper.reset()

    def force_unlock(self) -> None:
        """
        Forces the device to unlock without entering a password.<br>
        Doesn't reset the data available through the `gatekeeper` property.
        """
        self._gatekeeper.force_unlock()


class DeviceBuilder:
    """
    Class for build `Device` instances.<br>
    Since all settables are optional, creating an instance and calling `build()`

    >>> DeviceBuilder.new().build()

    will return a device with no keyboard, no password, no password rules,
    no max unlock attempts, and no timeout.

    All public methods (except `build()`) are chainable:
    >>> from shouldersurfscore.equipment.components import Components
    >>> from shouldersurfscore.classes.passwordrules import VariableLengthPasswordRule
    >>> device = Builder.new().set_keyboard(Components.get_standard_keyboard())
    .set_password("yeehaw")
    .add_password_rule(VariableLengthPasswordRule(5, 10))
    .set_max_unlock_attempts(5)
    .build()

    This would create a device with a standard U.S. qwerty keyboard,
    an initial password of "yeehaw",
    a password rule that says device passwords must be between 5 and 10 characters (inclusive),
    and a lockout mechanism that goes into effect after 5 unsuccessful unlock attempts.

    When a keyboard is set, an implicit rule is added to the device's password validation
    that only allows passwords whose characters are present on the keyboard.<br>
    If a password is set that violates this rule or any supplied rules,
    an `InvalidPasswordError` will be raised when `build()` is called.
    """

    def __init__(self) -> None:
        """
        Initialize a builder in its default state.
        """
        self._keyboard: Keyboard | None = None
        self._timeout: Timeout | None = None
        self._max_unlock_attempts: int | None = None
        self._password_rules: list[PasswordRule] = []
        self._password: str | None = None
        self._typeable_characters_rule: TypeableCharactersPasswordRule | None = None

    @classmethod
    def new(cls: type[Self]) -> Self:
        """
        Convenience method so a `Builder` object can be chained at creation
        since `__init__` can only return `None`.

        >>> device = Builder.new().add_password("yeehaw").build()

        instead of

        >>> builder = Builder()
        >>> device = builder.add_password("yeehaw").build()

        Returns
        -------
        DeviceBuilder
            A new default builder instance.
        """
        builder = cls()
        return builder

    def set_keyboard(self, keyboard: Keyboard | None) -> Self:
        """
        Set the keyboard for the device.

        A password rule will be derived from the characters on `keyboard`
        that will prohibit any passwords using characters
        that can't be typed with the given keyboard.

        Parameters
        ----------
        keyboard : Keyboard | None
            The keyboard to use for the device.

        Returns
        -------
        DeviceBuilder
            This builder instance for method chaining.
        """
        self._keyboard = keyboard
        # Ensure any potential passwords are actually typeable with the assigned keyboard.
        self._typeable_characters_rule = TypeableCharactersPasswordRule(
            keyboard.characters if keyboard else ""
        )
        return self

    def set_timeout(self, timeout: Timeout | None) -> Self:
        """
        Set the timeout object to be used by the device's gatekeeper.

        Parameters
        ----------
        timeout : Timeout | None
            The timeout instance to use.

        Returns
        -------
        DeviceBuilder
            This builder instance for method chaining.
        """
        self._timeout = timeout
        return self

    def set_max_unlock_attempts(self, max_attempts: int | None) -> Self:
        """
        Set the max unlock attempts before the device will go into lockout.

        Parameters
        ----------
        max_attempts : int | None
            The number of max attempts.<br>
            If `None`, the device will never go into lockout.

        Returns
        -------
        DeviceBuilder
            This builder instance for method chaining.
        """
        self._max_unlock_attempts = max_attempts
        return self

    def set_password_rules(self, rules: list[PasswordRule]) -> Self:
        """
        Set the password rules the device should use.<br>
        This will overwrite any previously added rules except
        for the keyboard derived typeable characters rule.

        Parameters
        ----------
        rules : list[PasswordRule]
            A list of password rules.

        Returns
        -------
        DeviceBuilder
            This builder instance for method chaining.
        """
        self._password_rules = rules
        return self

    def add_password_rule(self, rule: PasswordRule) -> Self:
        """
        Add a password rule to the set of rules the device will use.

        Parameters
        ----------
        rule : PasswordRule
            The rule to add

        Returns
        -------
        DeviceBuilder
            This builder instance for method chaining.
        """
        self._password_rules.append(rule)
        return self

    def set_password(self, password: str | None) -> Self:
        """
        Set the initial password for the device.<br>
        If the given password violates any of the password rules
        for the device, the `build()` method will raise an `InvalidPasswordError`.

        Parameters
        ----------
        password : str | None
            The password to set.

        Returns
        -------
        DeviceBuilder
            This builder instance for method chaining.
        """
        self._password = password
        return self

    def _add_typeable_characters_rule(self) -> None:
        """
        Add the keyboard derived typeable characters rule to the rule set.
        """
        if self._typeable_characters_rule:
            # Put at the front so it's checked first
            # If you can't type the password, doesn't matter if it violates other rules or not
            self._password_rules.insert(0, self._typeable_characters_rule)

    def build(self) -> Device:
        """
        Build the device.

        Returns
        -------
        Device
            The assembled device.

        Raises
        ------
        InvalidPasswordError
            If a password has been set that violates any password rules.
        """
        self._add_typeable_characters_rule()
        password_validator = PasswordValidator(self._password_rules)
        # If a password is set, check it against the rules
        if self._password and password_validator.is_invalid(self._password):
            raise InvalidPasswordError.from_password(self._password)
        gatekeeper = GateKeeper(
            self._password, self._max_unlock_attempts, self._timeout
        )
        device = Device(self._keyboard, gatekeeper, password_validator)
        return device

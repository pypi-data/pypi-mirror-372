import abc
from collections.abc import Iterable, Sequence

from typing_extensions import override

from shouldersurfscore.classes.key import Key


class PasswordRule(abc.ABC):
    """
    Interface for defining password validation rules.

    Implementing classes only need to implement the following method:
    `is_valid(self, password:str) -> bool`

    Example
    -------
    >>> class LengthRule(PasswordRule):
    >>>     def __init__(self, min_length:int, max_length: int):
    >>>         self.min_length = min_length
    >>>         self.max_length = max_length
    >>>
    >>>     def is_valid(self, password: str) -> bool:
    >>>         return self.min_length <= len(password) <= self.max_length
    """

    @abc.abstractmethod
    def is_valid(self, password: str) -> bool:
        """
        Returns whether the given password satisfies this rule.

        Parameters
        ----------
        password : str
            The password to test.

        Returns
        -------
        bool
            Whether this password satisfies the rule or not.

        """


class VariableLengthPasswordRule(PasswordRule):
    """
    Implements checking a password's length against a minimum length and an optional maximum length.
    """

    def __init__(self, min_length: int = 1, max_length: int | None = None) -> None:
        """
        Initialize the instance.

        Parameters
        ----------
        min_length : int, optional
            The minimum password length, by default 1.
        max_length : int | None, optional
            The maximum password length, by default None.

        Raises
        ------
        ValueError
            If `min_length` is less than 1 or less than `max_length`, if it is provided.

            If `max_length` is provided and is less than `min_length`.
        """
        self._min_length: int = 1
        self._max_length: int | None = None
        self.min_length = min_length
        self.max_length = max_length

    @property
    def min_length(self) -> int:
        """The minimum length for a password."""
        return self._min_length

    @min_length.setter
    def min_length(self, length: int) -> None:
        """
        Sets the minimum password length.

        Parameters
        ----------
        length : int
            The new minimum length

        Raises
        ------
        ValueError
            If the given length is less than 1 or less than `max_length` (if it is set).
        """
        if length < 1:
            raise ValueError("Value for min_length must be greater than 0.")
        if self.max_length is not None and length > self.max_length:
            raise ValueError("Value for min_length can't be greater than max_length.")
        self._min_length = length

    @property
    def max_length(self) -> int | None:
        """
        The maximum length for a password.

        If `None`, passwords can be any length, provided they aren't shorter than `min_length`.
        """
        return self._max_length

    @max_length.setter
    def max_length(self, length: int | None) -> None:
        """
        Sets the maximum password length.

        Parameters
        ----------
        length : int | None
            The new maximum length.

        Raises
        ------
        ValueError
            If `length` is not `None` and less than `min_length`.
        """
        if length is not None and length < self.min_length:
            raise ValueError("Value for max_length can't be less than min_length.")
        self._max_length = length

    @override
    def is_valid(self, password: str) -> bool:
        length: int = len(password)
        if self.max_length is None:
            return self.min_length <= length
        return self.min_length <= length <= self.max_length


class FixedLengthPasswordRule(PasswordRule):
    """
    Implements checking if a password's length is one of one or more discrete lengths,
    such as when a password is PIN based.
    """

    def __init__(self, lengths: Iterable[int]) -> None:
        """
        Initialize the instance.

        Parameters
        ----------
        lengths : Iterable[int]
            The acceptable lengths a password can be.

        Raises
        ------
        ValueError
            If `lengths` is an empty iterable.
        """
        if not lengths:
            raise ValueError("`lengths` cannot be empty.")
        self._lengths: set[int] = set(lengths)

    @override
    def is_valid(self, password: str) -> bool:
        return len(password) in self._lengths


class ProhibitedPasswordRule(PasswordRule):
    """
    Implements checking a password against a list of prohibited passwords,
    optionally case sensitive and/or partially matched.

    If the partial matching option is set to `True` and "teapot" is in the list of prohibited passwords,
    then "teapotteapot" will be considered an ivalid password.<br>
    If the partial matching option is set to `False` then "teapotteapot" would be considered valid.
    """

    def __init__(
        self,
        prohibited_passwords: Iterable[str],
        case_sensitive: bool = False,
        partial_matching: bool = True,
    ) -> None:
        """
        Initialize the instance.

        Parameters
        ----------
        prohibited_passwords : Sequence[str]
            A list of prohibited passwords.
        case_sensitive : bool, optional
            Whether the checks should be case sensitive or not, by default False.
        partial_matching: bool, optional
            Whether passwords in `prohibited_passwords` can be used as substrings
            to instead of exact matches, by default True.
        """
        self._case_sensitive: bool = case_sensitive
        self._prohibited_passwords: set[str]
        self._partial_matching: bool = partial_matching
        if case_sensitive:
            self._prohibited_passwords = set(prohibited_passwords)
        else:
            self._prohibited_passwords = set(
                password.lower() for password in prohibited_passwords
            )

    @override
    def is_valid(self, password: str) -> bool:
        if not self._case_sensitive:
            password = password.lower()
        if not self._partial_matching:
            return password not in self._prohibited_passwords
        for prohibited in self._prohibited_passwords:
            if prohibited in password:
                return False
        return True


class NoSequentialKeysPasswordRule(PasswordRule):
    """
    Implements checking whether a password is a set of sequential characters.

    For a keyboard with the layout

    'qQ wW eE rR tT'

    'aA sS dD fF gG'

    'zZ xX cC vV bB'

    this would prohibit passwords like:

    'qwert'

    'qwerT'

    'qwertttt'

    'wer'

    'eRtAs'

    'Bvcx'
    """

    def __init__(self, keys: Sequence[Key]) -> None:
        """
        Initialize the instance.

        Parameters
        ----------
        keys : Iterable[Key]
            A list of keys that can be used for a password
            in the order they appear on the keyboard
            from top left to bottom right.

            e.g. where `kb` is an instance of `Keyboard`

        >>> rule = NoSequentialKeysPasswordRule(kb.keys)

            Calling `is_valid` on a password that contains characters
            not in these keys will raise a `KeyError`.
        """
        # Values serve as indicies
        # Using a dict so that primary value and shift value have the same index
        self._keys: dict[str, int] = {}
        for i, key in enumerate(keys):
            self._keys[key.value] = i
            if key.shift_value:
                self._keys[key.shift_value] = i

    @override
    def is_valid(self, password: str) -> bool:
        # ? Should repeated keys or repeated keys where shift is held for one still fail validity check?
        # ? Should reverse sequential order also get flagged?
        for i, ch in enumerate(password[1:]):
            diff: int = self._keys[ch] - self._keys[password[i]]
            # if diff is -1, then keys are reverse sequential
            # if 0 they're the same key (primary or shift value)
            # if 1 then forward sequential
            if diff < -1 or diff > 1:
                return True
        return False


class NoMonoCharacterPasswordRule(PasswordRule):
    """
    Implements a rule that rejects passwords made up of only one repeated character.

    The implementation is case-insensitive.

    Note: A single character password will return as valid.
    Use one of the length rules to enforce this criteria.
    """

    @override
    def is_valid(self, password: str) -> bool:
        # ? Should lower the upper case count as invalid?
        return len(password) == 1 or len(set(password.lower())) != 1


class ValidCharactersPasswordRule(PasswordRule):
    """
    Implements a rule that rejects passwords containing characters not in the given set.
    """

    def __init__(self, characters: str) -> None:
        """
        Initialize the instance with set of valid characters.

        Parameters
        ----------
        characters : str
            The characters a valid password can contain.
        """
        self._characters: str = characters

    @override
    def is_valid(self, password: str) -> bool:
        return all(ch in self._characters for ch in password)

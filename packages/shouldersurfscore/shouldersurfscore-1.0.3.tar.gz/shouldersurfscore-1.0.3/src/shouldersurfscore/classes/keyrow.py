from collections.abc import Iterable, Iterator, Sequence, Sized

from typing_extensions import Self

from shouldersurfscore.classes.key import Key
from shouldersurfscore.classes.point import Point


class KeyRow(Iterable[Key], Sized):
    """
    Represents a Row of `Key`s.

    Supports the `Iterable` and `Sized` protocols, as well as indexing.

    e.g.
    >>> row = KeyRow.from_characters("asdfg")
    >>> print(len(row))
    5
    >>> for key in row:
    >>>   print(key)
    'aA'
    'sS'
    'dD'
    'fF'
    'gG'
    >>> print(key[0])
    'aA'
    >>> print(key[-1])
    'gG'
    """

    def __init__(self, keys: Sequence[Key]) -> None:
        """
        Initialize this row with a sequence of `Key` instances.

        Key positions will be overwritten such that the `x` component
        is equivalent to the key index and the `y` component is `0`.

        Parameters
        ----------
        keys : Sequence[Key]
            The keys that make up this row.
        """
        self._keys: list[Key] = []
        self.keys = keys
        # counter for iterable implementation
        self._i: int = 0

    def __add__(self, row: Self) -> Self:
        return type(self)(self.keys + row.keys)

    def __iadd__(self, row: Self) -> Self:
        return self + row

    def __getitem__(self, index: int) -> Key:
        return self.keys[index]

    def __iter__(self) -> Iterator[Key]:
        self._i = 0
        return self

    def __len__(self) -> int:
        return len(self.keys)

    def __next__(self) -> Key:
        if self._i < len(self):
            key: Key = self.keys[self._i]
            self._i += 1
            return key
        raise StopIteration

    def __str__(self) -> str:
        return " ".join((str(key) for key in self))

    @property
    def keys(self) -> list[Key]:
        """The keys in this row."""
        return self._keys

    @keys.setter
    def keys(self, keys: Sequence[Key]) -> None:
        """
        Replaces the keys in this row with a new set of keys
        and overwrites the positions of the added keys.

        Parameters
        ----------
        keys : Sequence[Key]
            The new set of keys that should make up this row.
        """
        self._keys = list(keys)
        for i, key in enumerate(self):
            key.position = Point(i, 0)

    def append(self, key: Key) -> None:
        """
        Add a new key to the row.

        Its `x` value will be `1` plus the previous key's `x` component
        and its `y` value will be `0`.

        Parameters
        ----------
        key : Key
            The key to append to the row.
        """
        self.keys.append(key)
        self.keys[-1].position.x = self.keys[-2].position.x + 1
        self.keys[-1].position.y = 0

    def extend(self, row: Self) -> None:
        """
        Add the keys from another row to the end of this row.

        Parameters
        ----------
        row : KeyRow
            The row of keys to add to this row.
        """
        for key in row:
            self.append(key)

    @classmethod
    def from_characters(cls: type[Self], characters: str) -> Self:
        """
        Initialize a `KeyRow` from a string of characters.

        Parameters
        ----------
        string : str
            The characters that should compose this `KeyRow`.

            Each character is assumed to be equivalent to one `Key`.

            If it is needed to specify shift values for the keys,
            use the contructor, `from_character_pairs()`, or `append()` methods.

        Returns
        -------
        KeyRow
            A new `KeyRow` containing keys derived from `string`.
        """
        return cls([Key(ch) for ch in characters])

    @classmethod
    def from_character_pairs(cls: type[Self], characters: str) -> Self:
        """
        Initialize a `KeyRow` from a string of characters
        where each pair is interpretted to be the primary value
        and the shift value, respectively, for each key.

        >>> row = KeyRow.from_character_pairs("1!2@3#4$5%")
        >>> row[0].value
        '1'
        >>> row[0].shift_value
        '!'
        >>> row[-1].value
        '5'
        >>> row[-1].shift_value
        '%'

        Parameters
        ----------
        string : str
            The string of characters to build the row from.

        Returns
        -------
        KeyRow
            A new `KeyRow` containing keys derived from `string`.

        Raises
        ------
        ValueError
            If the number of characters isn't divisible by 2.
        """
        if len(characters) % 2:
            raise ValueError("The number of characters must be divisible by 2.")
        pairs: list[tuple[str, str]] = [
            (characters[i], characters[i + 1]) for i in range(0, len(characters) - 1, 2)
        ]
        return cls([Key(v, s) for v, s in pairs])

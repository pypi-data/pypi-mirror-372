import itertools
from collections.abc import Sequence
from copy import copy

from typing_extensions import Self

from shouldersurfscore.classes.bounds import Bounds
from shouldersurfscore.classes.key import Key
from shouldersurfscore.classes.keyrow import KeyRow
from shouldersurfscore.classes.point import Point


class Keyboard:
    """
    Represents a keyboard.

    When adding rows to this keyboard, each new row is considered to be added under the previous row.
    e.g.
    >>> keyboard = Keyboard()
    >>> keyboard.add_row_from_characters("qwer").add_row_from_characters("asdf")
    >>> print(keyboard)
    'qQ wW eE rR'
    'aA sS dD fF'

    The geometric space of the keyboard is considered to be in quadrant 4 of the cartesian plane.

    The top left of the keyboard ('q' in the above example) is at `(0, 0)`
    and the bottom right of the keyboard ('f' in the above example) is at `(3, -1)`.

    Horizontal offsets can be specified when adding a row:
    >>> keyboard.add_row_from_characters("zxcv", 1)
    >>> print(keyboard)
    'qQ wW eE rR'
    'aA sS dD fF'
    '   zZ xX cC vV'

    The bottom right ('v') is at `(4, -2)`.

    `Key` objects with be looked up with either a string character or a `Point` instance.
    >>> keyboard = Keyboard()
    >>> keyboard.add_row_from_characters("asdf")
    >>> keyboard.get_key("a").shift_value
    'A'
    >>> keyboard.get_key("A").value
    'a'
    >>> keyboard.get_key(Point(3, 0)).value
    'f'

    Keys can be looked up with index notation:
    >>> keyboard["d"].shift_value
    'D'
    >>> keyboard[Point(2, -1)].value
    'd'

    Characters and `Point`s can be checked for membership with the `in` operator:
    >>> "d" in keyboard
    True
    >>> "+" in keyboard
    False

    All methods that look up keys will raise an exception if the key doesn't exist on this keyboard.
    """

    def __init__(self) -> None:
        self._rows: list[KeyRow] = []
        # Serves `Key` lookup by string character.
        # If a key has a shift value, that should be a separate key
        # in the map pointing to the same `Key` object.
        self._key_map: dict[str, Key] = {}
        # Serves `Key` lookup by physical location on the keyboard.
        self._position_map: dict[Point, Key] = {}
        # Serves row and column index lookup by key.
        # The `y` of the corresponding `Point` will be the index of the row the key belongs to.
        # The `x` will be the index of the key within that row.
        self._key_to_index_map: dict[Key, Point] = {}
        # Serves key lookup by column and row index as a `Point`.
        self._index_to_key_map: dict[Point, Key] = {}
        self._num_keys: int = 0
        self._num_rows: int = 0

    def __getitem__(self, item: str | Point) -> Key:
        if isinstance(item, str):
            return self._key_map[item]
        return self._position_map[item]

    def __str__(self) -> str:
        return "\n".join((" " * int(row[0].position.x)) + str(row) for row in self.rows)

    def __contains__(self, item: str | Point) -> bool:
        if isinstance(item, str):
            return item in self._key_map
        return item in self._position_map

    @property
    def characters(self) -> str:
        """All characters on this keyboard."""
        return "".join(self._key_map.keys())

    @property
    def keys(self) -> list[Key]:
        """All keys on this keyboard in left to right, top to bottom order."""
        return [key for row in self.rows for key in row]

    @property
    def num_keys(self) -> int:
        """The total number of keys on this keyboard."""
        return self._num_keys

    @property
    def num_rows(self) -> int:
        """The number of rows on this keyboard."""
        return self._num_rows

    @property
    def rows(self) -> list[KeyRow]:
        """The rows of this keyboard."""
        return self._rows

    def _add_to_maps(self, key: Key, column_index: int, row_index: int) -> None:
        """
        Add a key to the internal map structures of this keyboard.

        Parameters
        ----------
        key : Key
            The key to add.
        """
        self._key_map[key.value] = key
        self._position_map[key.position] = key
        index = Point(column_index, row_index)
        self._key_to_index_map[key] = index
        self._index_to_key_map[index] = key
        if key.shift_value:
            self._key_map[key.shift_value] = key

    def add_row(self, row: KeyRow, horizontal_offset: float = 0) -> Self:
        """
        Add a row of keys to this keyboard

        Parameters
        ----------
        row : KeyRow
            The row to add.
        horizontal_offset : float, optional
            The horizontal offset for this row, by default 0.

        Returns
        -------
        Keyboard
            Returns this instance so that calls to `add_row` can be chained together.
        """
        self._rows.append(row)
        self._num_rows += 1
        self._num_keys += len(row)
        y: int = -1 * (self.num_rows - 1)
        for i, key in enumerate(self._rows[-1]):
            key.position = Point(i + horizontal_offset, y)
            self._add_to_maps(key, i, -1 * y)
        return self

    def add_row_from_characters(
        self, characters: str, horizontal_offset: float = 0
    ) -> Self:
        """
        Adds a row to the keyboard from a string of characters.

        Parameters
        ----------
        characters : str
            The characters to add.

            Each character is mapped to one key.

            If the character is a lowercase alphabetic character,
            the uppercase version will be added as the key's shift value.
        horizontal_offset : float, optional
            The horizontal offset for the new row, by default 0.

        Returns
        -------
        Keyboard
            Returns this instance so that calls can be chained together.
        """
        return self.add_row(KeyRow.from_characters(characters), horizontal_offset)

    def add_rows(
        self, rows: Sequence[KeyRow], horizontal_offsets: Sequence[float] | None = None
    ) -> None:
        """
        Add multiple rows to the keyboard in top-down order.

        Parameters
        ----------
        rows : Sequence[KeyRow]
            The rows to be added.
        horizontal_offsets : Sequence[float] | None, optional
            The offsets for each row.

            If provided, it must have the same length as `rows`.

        Raises
        ------
        ValueError
            When `horizontal_offsets` is provided but the length doesn't match `rows`.
        """
        if horizontal_offsets and len(rows) != len(horizontal_offsets):
            raise ValueError(
                f"`rows` and `horizontal_offsets` must be the same length."
                + f"\nNot {len(rows)=} and {len(horizontal_offsets)=}."
            )
        if not horizontal_offsets:
            horizontal_offsets = [0] * len(rows)
        for row, offset in zip(rows, horizontal_offsets):
            self.add_row(row, offset)

    def add_rows_from_character_sets(
        self,
        character_sets: Sequence[str],
        horizontal_offsets: Sequence[float] | None = None,
    ) -> None:
        """
        Add multiple rows to the keyboard in top-down order.

        Parameters
        ----------
        character_sets : Sequence[str]
            Each string represents a row to be added.

            Each character from a set is mapped to one key.

            If the character is a lowercase alphabetic character,
            the uppercase version will be added as the key's shift value.
        horizontal_offsets : Sequence[float] | None, optional
            The offsets for each row.

            If provided, it must have the same length as `character_sets`.

        Raises
        ------
        ValueError
            When `horizontal_offsets` is provided but the length doesn't match `character_sets`.
        """
        self.add_rows(
            [KeyRow.from_characters(row) for row in character_sets], horizontal_offsets
        )

    def get_bounds(self) -> Bounds:
        """
        The bounding box of this keyboard.

        Returns
        -------
        Bounds
            The bounding box of this keyboard.
        """
        return Bounds.from_points([key.position for key in self.keys])

    def get_distance(self, char1: str, char2: str) -> float:
        """
        The Euclidean distance between two keys on this keyboard.

        Parameters
        ----------
        char1 : str
            The first key, can be the primary value or the shift value.
        char2 : str
            The second key, can be the primary value or the shift value.

        Returns
        -------
        float
            The Euclidean distance between the key matching `char1` and the key matching `char2`.

        Raises
        ------
        KeyError
            If either `char1` or `char2` doesn't exist on this keyboard.
        """
        return self[char1].distance(self[char2])

    def index(self, character: str) -> Point:
        """
        Returns the [column][row] index of the key for the given character.

        Parameters
        ----------
        character : str
            The character to return the index for.

        Returns
        -------
        Point
            The 2D index of the key for `character`.<br>
            The `x` field is the column index and
            the `y` field is the row index.<br>
            Note: The returned object is a copy.
            Altering it will not affect the one
            maintained by this instance.

        Raises
        ------
        KeyError
            If `character` doesn't exist on this keyboard.
        """
        return copy(self._key_to_index_map[self[character]])

    def get_key(self, identifier: str | Point) -> Key:
        """
        Look up the key matching `identifier`.

        Parameters
        ----------
        identifier : str | Point
            Can either be a character or a `Point` object.

            If a string, the identifier can be either the primary value
            or the shift value of the key to look up.

        Returns
        -------
        Key
            The corresponding `Key` object.

        Raises
        ------
        KeyError
            If there is no key matching `identifier`.
        """
        return self[identifier]

    def get_key_bounds(self, sequence: str) -> Bounds:
        """
        The bounding box for the given character sequence.

        Parameters
        ----------
        sequence : str
            The characters corresponding to keys that should define the bounding box.

        Returns
        -------
        Bounds
            The bounding box for the keys corresponding to the characters in `sequence`.

        Raises
        ------
        KeyError
            If any character in `sequence` is not on this keyboard.
        """
        return Bounds.from_points([self[ch].position for ch in sequence])

    def get_key_relative_to_character(
        self, character: str, horizontal_offset: int, vertical_offset: int
    ) -> Key | None:
        """
        Returns the key that is `horizontal_offset`x`vertical_offset` keys
        away from the key for the given character.<br>
        The offsets are in terms of number of keys, not physical distance.<br>
        For example, on a standard U.S. qwerty keyboard,
        `get_key_relative_to_character("a", 2, 0)` would return the key for "d"
        and `get_key_relative_to_character("a", 2, -1)` would return the key for "c".

        Parameters
        ----------
        character : str
            The character to find the key relative to.
        horizontal_offset : int
            The number of keys to the left or right.
        vertical_offset : int
            The number of keys up or down.

        Returns
        -------
        Key | None
            The key specified by the offset from the key for `character`.<br>
            If that offset would be off this keyboard, `None` will be returned.

        Raises
        ------
        KeyError
            If `character` doesn't exist on this keyboard.
        """
        index: Point = self.index(character)
        # -1 * v.o. b/c going "up" is going down row indicies
        index += Point(horizontal_offset, -1 * vertical_offset)
        return self._index_to_key_map.get(index, None)

    def get_keys_within_bounds_of_character(
        self, character: str, bounds: Bounds
    ) -> list[Key]:
        """
        Get keys that are within the given bounds centered on the given character.<br>
        The bounds are in terms of number of keys, not physical distance.<br>
        For example, on a standard U.S. qwerty keyboard,
        `get_keys_within_bounds_of_character("s", Bounds(-1, 1, 1, -1))`
        would return the keys for characters "qweadzxc"
        and `get_keys_within_bounds_of_character("s", Bounds(-1, 1, 2, -1))`
        would return the keys for characters "qweradfzxcv".

        Parameters
        ----------
        character : str
            The character to center the bounding box around.
        bounds : Bounds
            The bounds around the key for `character` from which to return keys.

        Returns
        -------
        list[Key]
            The keys within the bounding box of `character`.

        Raises
        ------
        KeyError
            If `character` doesn't exist on this keyboard.
        """
        reference_key: Key = self[character]
        reference_index: Point = self.index(character)
        # convert y b/c "going up" is decreasing index
        reference_index.y *= -1
        bounds = bounds.shifted_by(reference_index)
        adjacent_keys: list[Key] = []
        for key in self.keys:
            index: Point = self.index(key.value)
            index.y *= -1
            if bounds.contains(index) and key != reference_key:
                adjacent_keys.append(key)
        return adjacent_keys

    def get_path(self, sequence: str) -> list[Point]:
        """
        Calculates the vector sequence to get from each key to the next key in `sequence`.

        Parameters
        ----------
        sequence : str
            A sequence of characters.

        Returns
        -------
        list[Point]
            `Point` objects representing the vector sequence to get from one key to the next.

        Raises
        ------
        KeyError
            If any character in `sequence` doesn't exist on this keyboard.

        Examples
        --------
        >>> keyboard = Keyboard()
        >>> keyboard.add_rows_from_characterss(["asdf", "zxcv"])
        >>> print(keyboard)
        'aA sS dD fF'
        'zZ xX cC vV'
        >>> ", ".join([str(vector) for vector in keyboard.get_path("AxCf")])
        '(1, -1), (1, 0), (1, 1)'
        """
        return [
            self.get_vector(ch1, ch2) for (ch1, ch2) in itertools.pairwise(sequence)
        ]

    def get_path_bounds(self, sequence: str) -> Bounds:
        """
        Calculates the bounds of the vector path that points from each key in `sequence` to the next.

        i.e. the max left, right, up, and down displacement of the vector list
        defining the path taken by `seqeuence`.

        Parameters
        ----------
        sequence : str
            A sequence of characters.

        Returns
        -------
        Bounds
            The bounding box for the set of vectors defined by the path traversed by `sequence`.

        Raises
        ------
        KeyError
            If any character in `sequence` doesn't exist on this keyboard.

        Examples
        --------
        >>> keyboard = Keyboard()
        >>> k.add_rows_from_characterss(["qwert", "asdfg", "zxcvb"])
        >>> print(k)
        'qQ wW eE rR tT'
        'aA sS dD fF gG'
        'zZ xX cC vV bB'
        >>> sequence = "qxzt"
        >>> keyboard.get_path(s)
        [Point(x=1, y=-2), Point(x=-1, y=0), Point(x=4, y=2)]
        >>> keyboard.get_path_bounds(sequence)
        Bounds(left=-1, top=2, right=4, bottom=-2)
        """
        return Bounds.from_points(self.get_path(sequence))

    def get_position(self, character: str) -> Point:
        """
        The position of the key corresponding to `character`.

        Parameters
        ----------
        character : str
            The character of the key to get the position for.

        Returns
        -------
        Point
            The position of `character`.

        Raises
        ------
        KeyError
            If `character` doesn't exist on this keyboard.
        """
        return self[character].position

    def get_vector(self, char1: str, char2: str) -> Point:
        """
        The vector the points from the first key to the second key.

        Parameters
        ----------
        char1 : str
            The character for the first key.
        char2 : str
            The character for the second key.

        Returns
        -------
        Point
            The vector pointing from the first key to the second.

        Raises
        ------
        KeyError
            If either `char1` or `char2` doesn't exist on this keyboard.
        """

        return self[char1].vector(self[char2])

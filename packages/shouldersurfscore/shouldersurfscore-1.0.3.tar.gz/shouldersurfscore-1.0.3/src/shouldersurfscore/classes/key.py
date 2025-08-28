import string

from typing_extensions import Self

from shouldersurfscore.classes.point import Point


class Key:
    """
    Represents a key having a primary `value` and an optional `shift_value` on an input device.
    """

    def __init__(
        self, value: str, shift_value: str | None = None, position: Point | None = None
    ) -> None:
        """
        Initializes a new `Key`.

        Parameters
        ----------
        value : str
            The string value of this key when pressed.
        shift_value : str | None, optional
            The string value of this key when pressed while 'shift' is held.

            If not given and `value` is a lower case alphabetic character,
            this will be set to the upper case version of `value`.

            i.e. `Key("a").shift_value` will be "A".
        position : Point | None, optional
            The position of this key.
            If not provided, it will be set to `(0, 0)`.
        """
        self._value: str
        self._shift_value: str | None
        self.set_key_value(value, shift_value)
        self.position: Point = position if position else Point(0, 0)

    def __str__(self) -> str:
        text: str = self.value
        if self.shift_value:
            text += self.shift_value
        return text

    @property
    def shift_value(self) -> str | None:
        """
        The value, if it has one, of this key when pressed with "shift".
        """
        return self._shift_value

    @property
    def value(self) -> str:
        """
        The value of this key when pressed.
        """
        return self._value

    def distance(self, key: Self) -> float:
        """
        The distance between this key and another.

        Parameters
        ----------
        key : Key
            Another key.

        Returns
        -------
        float
            The distance between the two keys.
        """
        return self.position.distance(key.position)

    def set_key_value(self, value: str, shift_value: str | None = None) -> None:
        """
        Set this key's value.

        If `shift_value` is not provided and `value` is a lowercase alphabetic character,
        `shift_value` will default to the upper case version of `value`.

        Parameters
        ----------
        value : str
            The key character.
        shift_value : str | None, optional
            The key character when used with the shift key, by default None
        """
        self._value = value
        self._shift_value = (
            value.upper()
            if shift_value is None and value in string.ascii_lowercase
            else shift_value
        )

    def vector(self, key: Self) -> Point:
        """
        The vector pointing from this key to another.

        Parameters
        ----------
        key : Key
            Another key.

        Returns
        -------
        Point
            The vector from this key to `key`.
        """
        return self.position.vector(key.position)

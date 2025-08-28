import math
from dataclasses import dataclass

from typing_extensions import Self


@dataclass
class Point:
    """
    Represents a point in a two dimensional space having `x` and `y` components.
    """

    x: float
    y: float

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Point):
            raise TypeError("Can only compare to other `Point` instances.")
        return self.x == value.x and self.y == value.y

    def __hash__(self) -> int:
        return hash(self.x) + hash(self.y)

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

    def __sub__(self, point: Self) -> Self:
        return type(self)(self.x - point.x, self.y - point.y)

    def __isub__(self, point: Self) -> Self:
        return self - point

    def __add__(self, point: Self) -> Self:
        return type(self)(self.x + point.x, self.y + point.y)

    def __iadd__(self, point: Self) -> Self:
        return self + point

    def as_tuple(self) -> tuple[float, float]:
        """
        Get this point as a tuple.

        Returns
        -------
        tuple[float, float]
            Returns the xy values of this point in the form `(x, y)`.
        """
        return (self.x, self.y)

    def distance(self, point: Self) -> float:
        """
        The Euclidean distance from this point to another.

        Parameters
        ----------
        point : Point
            Another point.

        Returns
        -------
        float
            The distance between this point and the given one.
        """
        return math.dist((self.x, self.y), (point.x, point.y))

    def vector(self, point: Self) -> Self:
        """
        The vector pointing from this point to the given one.

        Parameters
        ----------
        point : Point
            Another point.

        Returns
        -------
        Point
            The vector between this point and another.
        """
        return point - self

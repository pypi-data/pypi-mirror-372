from collections.abc import Sequence
from dataclasses import dataclass

from typing_extensions import Self

from shouldersurfscore.classes.point import Point


@dataclass(frozen=True)
class Bounds:
    """
    Immutable class representing a two dimensional bounding box.

    Raises
    ------
        ValueError
            If `left` is greater than `right` or `bottom` is greater than `top`.
    """

    left: float
    top: float
    right: float
    bottom: float

    def __post_init__(self):
        if self.left > self.right:
            raise ValueError(
                "Value for `right` must be greater than `left`."
                + f"\nNot {self.left=} and {self.right=}"
            )
        if self.bottom > self.top:
            raise ValueError(
                "Value for `top` must be greater than `bottom`."
                + f"\nNot {self.bottom=} and {self.top=}"
            )

    @property
    def bottom_left(self) -> Point:
        return Point(self.left, self.bottom)

    @property
    def bottom_right(self) -> Point:
        return Point(self.right, self.bottom)

    @property
    def top_left(self) -> Point:
        return Point(self.left, self.top)

    @property
    def top_right(self) -> Point:
        return Point(self.right, self.top)

    def contains(self, point: Point) -> bool:
        """
        Check if `point` is within the bounded space.

        Parameters
        ----------
        point : Point
            The point to check.

        Returns
        -------
        bool
            `True` if the point is within these bounds.
        """
        return self.left <= point.x <= self.right and self.bottom <= point.y <= self.top

    @classmethod
    def from_points(cls: type[Self], points: Sequence[Point]) -> Self:
        """
        Create a `Bounds` instance from a list of points.

        Parameters
        ----------
        points : Sequence[Point]
            The list of points that should be used to determine the bounding box.

        Returns
        -------
        Bounds
            The bounding box defined by the list of points.
        """
        xs: list[float] = []
        ys: list[float] = []
        for point in points:
            xs.append(point.x)
            ys.append(point.y)
        return cls(min(xs), max(ys), max(xs), min(ys))

    def shifted_by(self, point: Point) -> Self:
        """
        Returns a new instance that is shifted by the given point.
        >>> bounds = Bounds(-1, 1, 1, -1)
        >>> new_bounds = bounds.shifted_by(Point(5, 5))
        >>> new_bounds.bottom
        4
        >>> new_bounds.left
        4
        >>> new_bounds.top
        6
        >>> new_bounds.right
        6

        Parameters
        ----------
        point : Point
            The point describing how much to shift the box by.

        Returns
        -------
        Self
            A new shifted instance.
        """
        return type(self).from_points(
            [
                point + self.bottom_left,
                point + self.top_left,
                point + self.top_right,
                point + self.bottom_right,
            ]
        )

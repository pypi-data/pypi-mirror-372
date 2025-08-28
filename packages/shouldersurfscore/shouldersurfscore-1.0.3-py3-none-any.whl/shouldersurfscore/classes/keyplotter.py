from enum import Enum

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from shouldersurfscore.classes.keyboard import Keyboard


class KeyStyle(Enum):
    VALUE_ONLY = 1
    SHIFT_VALUE_ONLY = 2
    BOTH = 3


class KeyPlotter:
    """Class with static methods for producing matplotlib figures from keyboards."""

    @staticmethod
    def plot_keyboard(
        keyboard: Keyboard, key_style: KeyStyle = KeyStyle.BOTH
    ) -> Figure:
        """
        Create a plot of a keyboard.

        Parameters
        ----------
        keyboard : Keyboard
            The keyboard to plot.
        key_style : KeyStyle, optional
            Whether to show both values for a key or just one, by default KeyStyle.BOTH.

        Returns
        -------
        Figure
            A figure that can be modified or shown as is.
        """
        fig: Figure = plt.gcf()
        # TODO: Make key boxes have uniform size and space
        for key in keyboard.keys:
            xy: tuple[float, float] = key.position.as_tuple()
            value: str | None
            # stripping spaces to prevent boxes for what should be skipped key locations
            if key_style == KeyStyle.VALUE_ONLY:
                value = key.value.strip()
            elif key_style == KeyStyle.SHIFT_VALUE_ONLY:
                value = key.shift_value
            else:
                value = str(key).strip()
            if value != "":
                plt.plot(*xy)  # type: ignore
                plt.text(  # type: ignore
                    *xy,
                    s=value,  # type: ignore
                    ha="center",
                    va="center",
                    bbox={
                        "boxstyle": "round",
                        "color": (1, 1, 1),
                        "ec": (0, 0, 0),
                    },
                )
        plt.axis("off")  # type: ignore
        return fig

    @staticmethod
    def plot_entry(
        keyboard: Keyboard,
        entry: str,
        arrow_props: dict[str, str] = {},
        key_style: KeyStyle = KeyStyle.BOTH,
    ) -> Figure:
        """
        Create a plot of a key sequence on a keyboard.
        A sequence of arrows will be plotted from each key in `entry` to the next.

        Parameters
        ----------
        keyboard : Keyboard
            The keyboard to plot.
        entry : str
            The key sequence to plot.
        arrow_props : dict[str, str], optional
            Arguments to be passed to `matplotlib.pyplot.annotate` for styling arrows, by default {}.
        key_style : KeyStyle, optional
            Whether to show both values for a key or just one, by default KeyStyle.BOTH.

        Returns
        -------
        Figure
            A figure that can be modified or shown as is.

        Raises
        ------
        KeyError
            If any character in `entry` doesn't exist on `keyboard`.
        """
        fig: Figure = KeyPlotter.plot_keyboard(keyboard, key_style)
        default_arrow_props: dict[str, str] = {
            "arrowstyle": "-|>",
            "connectionstyle": "arc3,rad=.1",
        } | arrow_props
        for i, ch in enumerate(entry[:-1]):
            start: tuple[float, float] = keyboard.get_position(ch).as_tuple()
            stop: tuple[float, float] = keyboard.get_position(entry[i + 1]).as_tuple()
            plt.annotate(text="", xy=stop, xytext=start, arrowprops=default_arrow_props)  # type: ignore
        return fig

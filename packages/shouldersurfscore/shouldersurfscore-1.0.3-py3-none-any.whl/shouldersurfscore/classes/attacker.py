from shouldersurfscore.classes.device import Device
from shouldersurfscore.classes.guess_manager import GuessManager
from shouldersurfscore.classes.guessing_strategies import (
    GuessingStrategy,
    ObservedGuess,
)


class BreakInNotAttemptedError(Exception):
    """Error class for when action requiring a break attempt has invoked."""


class Attacker:
    """
    Represents an attacker that can try to break into a device using various strategies.
    """

    def __init__(self, strategies: list[GuessingStrategy]) -> None:
        """
        Initialize the attacker with a list of strategies to utilize.

        Parameters
        ----------
        strategies : list[GuessingStrategy]
            The strategies this attacker should use when attempting to break in to a device.<br>
            When calling `break_in()`, an `ObservedGuess` strategy instance will be
            prepended to the list.
        """
        self._strategies: list[GuessingStrategy] = [ObservedGuess()] + strategies
        # Initializing with empty list to avoid any computation/iteration
        # before the password validator is obtained from the device
        # being broken into.
        self._guesser: GuessManager = GuessManager("", [])
        self._break_in_attempted: bool = False

    @property
    def attempts_made(self) -> int:
        """The number of guess attempts made during the previous call to `break_in`."""
        return self._guesser.num_guesses_made

    @property
    def num_possible_guesses(self) -> int:
        """
        The number of possible guesses this attacker can make using their strategies.

        Raises
        ------
        BreakInNotAttemptedError
            If this property is accessed before `break_in` is called.
        """
        if not self._break_in_attempted:
            raise BreakInNotAttemptedError(
                "The number of possible guesses is unknown until `break_in` is called."
            )
        return self._guesser.num_possible_guesses

    def is_guess(self, guess: str) -> bool:
        """
        Whether this attacker would have guessed the given guess at some point.<br>
        i.e. would this attacker's guessing strategies have produced `guess`.

        Parameters
        ----------
        guess : str
            The guess to check for.

        Returns
        -------
        bool
            Whether the guess would have been guessed.

        Raises
        ------
        BreakInNotAttemptedError
            If this function is called before `break_in` is called.
        """
        if not self._break_in_attempted:
            raise BreakInNotAttemptedError(
                "If a password would be guessed is unknown until `break_in` is called."
            )
        return guess in self._guesser

    def index(self, guess: str) -> int | None:
        """
        The index of `guess` in this attacker's guess list.

        Parameters
        ----------
        guess : str
            The guess to return the index of.

        Returns
        -------
        int
            The index of `guess`.

        Raises
        ------
        BreakInNotAttemptedError
            If this function is called before `break_in` is called.
        """
        if not self._break_in_attempted:
            raise BreakInNotAttemptedError(
                "The index of a guess is unknown until `break_in` is called."
            )
        return self._guesser.index(guess)

    def break_in(self, device: Device, observed_password: str) -> bool:
        """
        Attempt to break into the given device.

        Parameters
        ----------
        device : Device
            The device to break into.
        observed_password : str
            The password the attacker observed.

        Returns
        -------
        bool
            Whether the break in was successful or not.
        """
        self._break_in_attempted = True
        self._guesser = GuessManager(
            observed_password,
            self._strategies,
            device.password_validator,
        )
        for guess in self._guesser:
            device.unlock(guess)
            if device.is_unlocked:
                return True
            if device.is_locked_out:
                return False
        return False

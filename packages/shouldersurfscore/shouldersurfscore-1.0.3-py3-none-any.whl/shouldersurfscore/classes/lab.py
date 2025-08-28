from shouldersurfscore.analysis.breakin_analysis import BreakInAnalysis
from shouldersurfscore.classes.attacker import Attacker
from shouldersurfscore.classes.device import Device
from shouldersurfscore.classes.guessing_strategies import GuessingStrategy


class Lab:
    """
    Class for running a break-in attempt on a device.
    """

    def __init__(
        self, device: Device, guessing_strategies: list[GuessingStrategy]
    ) -> None:
        """
        Initialize the lab with a device and a list of guessing strategies an attacker should use.

        Parameters
        ----------
        device : Device
            The device used in the experiment.
        guessing_strategies : list[GuessingStrategy]
            The guessing strategies to use.<br>
            An `ObservedGuess` instance will be automatically prepended to the list of strategies.
        """
        self._device: Device = device
        self._guessing_strategies: list[GuessingStrategy] = guessing_strategies

    def _set_password(self, password: str) -> None:
        """
        Sets a device's password and locks it without needing client intervention.<br>
        Resets device metrics.

        Parameters
        ----------
        device : Device
            The device to set the password for.
        password : str
            The password to set.
        """
        self._device.force_unlock()
        self._device.set_password(password)
        self._device.lock()

    def run(
        self,
        actual_password: str,
        observed_password: str,
    ) -> BreakInAnalysis:
        """
        Run a break-in attempt.

        This instance's device password will be automatically set to the provided password and
        its metrics will be reset prior to the break in attempt,
        i.e. the same device can be used for repeated invocations of this method.

        Parameters
        ----------
        actual_password : str
            The actual password for the device.
        observed_password : str
            The password observed by the attacker.

        Returns
        -------
        BreakInAnalysis
            The results of the break in attempt.
        """
        self._set_password(actual_password)
        attacker = Attacker(self._guessing_strategies)
        attacker.break_in(self._device, observed_password)
        password_index: int | None = attacker.index(actual_password)
        password_index_percent: float | None = (
            password_index / attacker.num_possible_guesses if password_index else None
        )
        return BreakInAnalysis(
            actual_password,
            observed_password,
            password_index,
            password_index_percent,
            self._device.gatekeeper.elapsed_time,
            self._device.is_unlocked,
        )

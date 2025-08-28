from shouldersurfscore.analysis.breakin_analysis import BreakInAnalysis
from shouldersurfscore.classes import guessing_strategies
from shouldersurfscore.classes.device import Device
from shouldersurfscore.classes.lab import Lab
from shouldersurfscore.equipment.devices import Devices


class InitialShoulderSurfScorePaperLab:
    @staticmethod
    def run(password: str, observed_password: str) -> BreakInAnalysis:
        device: Device = Devices.get_iphone()
        lab = Lab(
            device,
            [
                guessing_strategies.SwapAdjacentCharacters(),
                guessing_strategies.BruteForceGuessing(
                    device.keyboard.characters, [4, 6]
                ),
            ],
        )
        return lab.run(
            password,
            observed_password,
        )

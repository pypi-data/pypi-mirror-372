from shouldersurfscore.analysis.breakin_analysis import BreakInAnalysis
from shouldersurfscore.classes import guessing_strategies
from shouldersurfscore.classes.lab import Lab
from shouldersurfscore.equipment.devices import Devices


def test_lab():
    actual_pw = "1234"
    observed_pw = "1243"
    lab = Lab(
        Devices.get_iphone(),
        [
            guessing_strategies.SwapAdjacentCharacters(),
        ],
    )
    analysis = lab.run(
        actual_pw,
        observed_pw,
    )
    print()
    print(analysis)
    assert analysis.device_unlocked


def test_lab_no_success():
    actual_pw = "1234"
    observed_pw = "4335"
    lab = Lab(
        Devices.get_iphone(),
        [
            guessing_strategies.SwapAdjacentCharacters(),
        ],
    )
    analysis = lab.run(
        actual_pw,
        observed_pw,
    )
    print()
    print(analysis)
    assert not analysis.device_unlocked


def test_multiple_runs():
    # checking that things are set/reset properly between invocations
    device = Devices.get_iphone()
    observed_pws = ["6672", "1234"]
    actual_pws = ["8273", "1324"]
    analyses: list[BreakInAnalysis] = []
    assert device.keyboard
    lab = Lab(
        device,
        [
            guessing_strategies.SwapAdjacentCharacters(),
            guessing_strategies.BruteForceGuessing(
                device.keyboard.characters,
                [4],  # 6 is valid length, but this will speed up test
            ),
        ],
    )
    for actual, observed in zip(actual_pws, observed_pws):
        analyses.append(lab.run(actual, observed))

    assert analyses[0] != analyses[1]
    # first one should result in lock out
    assert not analyses[0].device_unlocked
    assert analyses[0].elapsed_time.total_seconds() > 0
    # second one should be successful w/o incurring timeouts
    assert analyses[1].device_unlocked
    assert analyses[1].elapsed_time.total_seconds() == 0
    print()
    print(*analyses, sep="\n")

import datetime

from shouldersurfscore.analysis.breakin_analysis import BreakInAnalysis


def test_analysis():
    analysis = BreakInAnalysis(
        "right",
        "wrong",
        1,
        0.5,
        datetime.timedelta(hours=1, minutes=7, seconds=33),
        True,
    )
    print()
    print(analysis)
    analysis2 = BreakInAnalysis.from_dict(analysis.asdict())
    assert analysis == analysis2
    print()
    print(analysis2)


def test_no_index():
    analysis = BreakInAnalysis(
        "right",
        "wrong",
        None,
        None,
        datetime.timedelta(hours=1, minutes=7, seconds=33),
        True,
    )
    print(analysis)

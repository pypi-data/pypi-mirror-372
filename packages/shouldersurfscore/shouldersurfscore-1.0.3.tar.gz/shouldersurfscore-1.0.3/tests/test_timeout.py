import datetime

import pytest

from shouldersurfscore.classes import timeouts


def test_delta_from_seconds():
    delta = timeouts.delta_from_seconds(1)
    assert delta.total_seconds() == 1
    delta = timeouts.delta_from_seconds(111.11)
    assert delta.total_seconds() == 111.11


def test_constant_timeout():
    with pytest.raises(ValueError):
        timeouts.ConstantTimeout(datetime.timedelta(seconds=-100))
    timeout = timeouts.ConstantTimeout()
    for _ in range(10):
        assert timeout.wait().total_seconds() == 0
        assert next(timeout).total_seconds() == 0
    timeout.reset()
    timeout = timeouts.ConstantTimeout(datetime.timedelta(seconds=100))
    for _ in range(10):
        assert next(timeout).total_seconds() == 100


def test_linear_timeout():
    with pytest.raises(ValueError):
        timeouts.LinearTimeout(datetime.timedelta(seconds=-1))
    with pytest.raises(ValueError):
        timeouts.LinearTimeout(
            datetime.timedelta(seconds=1), datetime.timedelta(seconds=-1)
        )
    initial = 5
    increment = 1
    timeout = timeouts.LinearTimeout(
        datetime.timedelta(seconds=increment), datetime.timedelta(seconds=initial)
    )
    for i in range(10):
        time = next(timeout)
        assert time.total_seconds() == (initial + (i * increment))
    timeout.reset()
    assert next(timeout).total_seconds() == initial


def test_arbitrary_timeout():
    with pytest.raises(ValueError):
        timeouts.ArbitraryTimeout([])
    with pytest.raises(ValueError):
        timeouts.ArbitraryTimeout([datetime.timedelta(-100)])
    deltas = [
        datetime.timedelta(seconds=0),
        datetime.timedelta(seconds=10),
        datetime.timedelta(seconds=23),
    ]
    timeout = timeouts.ArbitraryTimeout(deltas)
    total = sum(next(timeout).total_seconds() for _ in range(len(deltas)))
    assert total == sum(delta.total_seconds() for delta in deltas)
    for _ in range(10):
        assert next(timeout) == deltas[-1]
    timeout.reset()
    assert next(timeout) == deltas[0]

import pytest
from test_keyboard import run_plot_test

from shouldersurfscore.classes.keyplotter import KeyPlotter
from shouldersurfscore.equipment.components import Components


@pytest.mark.plot
def test_standard_keyboard():
    run_plot_test(KeyPlotter.plot_keyboard, Components.get_standard_keyboard())


@pytest.mark.plot
def test_standard_mobile_keyboard():
    run_plot_test(KeyPlotter.plot_keyboard, Components.get_standard_mobile_keyboard())


@pytest.mark.plot
def test_standard_keypad():
    run_plot_test(KeyPlotter.plot_keyboard, Components.get_standard_keypad())


@pytest.mark.plot
def test_standard_mobile_keypad():
    run_plot_test(KeyPlotter.plot_keyboard, Components.get_standard_mobile_keypad())


@pytest.mark.plot
def test_standard_pin_keypad():
    run_plot_test(KeyPlotter.plot_keyboard, Components.get_standard_pin_keypad())

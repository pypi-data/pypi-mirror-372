# `shouldersurfscore`

This library helps researchers in lab settings develop better metrics to understand the practical password guess quality of shoulder surfing and password guessing attacks.

The library provides the following (their complexity for you to use in parentheses):

- (Advanced): a nuanced set of classes to build an experiment environment including different keyboard layouts, device lockout patterns, and different styles of attackers that can help to better estimate different
- (Medium): predefined equipment to make it easier to get up and running (e.g. an iPhone, with common login restrictions).
- (Easy): defined scores to make it easier to reproduce other researchers' experiments (and when you're ready, hopefully yours too!).
- (Easy): implementations of a few other common metrics for assessing password quality.

## Installation

To install, simply use:

```console
pip install shouldersurfscore
```

## How-To Use

### Defined Labs

Pre-defined labs can be used to recreate scores used in others' experiments.

For example:

```python
from shouldersurfscore.defined_experiments.built_labs import InitialShoulderSurfScorePaperLab

analysis = InitialShoulderSurfScorePaperLab.run(
    actual_password='9163',
    observed_password='9613'
)
print(analysis)
```

```console
Break In Analysis
------------------
actual_password: 9163
observed_password: 9613
password_index: 2
password_index_percent: 1.9801980198019803e-06
elapsed_time: 0s
device_unlocked: True
```

### Other Metrics

### Predefined Objects

```python
from shouldersurfscore.analysis.breakin_analysis import BreakInAnalysis
from shouldersurfscore.classes import guessing_strategies
from shouldersurfscore.classes.lab import Lab
from shouldersurfscore.equipment.devices import Devices

device = Devices.get_iphone()
# Define strategies
pin_lengths = [4, 6]
# If the observed password doesn't work
# then all possible passwords will be tried in sequential order
# until successful or device goes into lock out.
strategies: list[guessing_strategies.GuessingStrategy] = [
    # Initialize brute force method with which characters are valid
    # and which pin lengths are valid
    guessing_strategies.BruteForceGuessing(device.keyboard.characters, pin_lengths)
]
password = "2290"
observed_password = "9163"
analysis = Lab.run(device, strategies, password, observed_password)
print(analysis)
```

```console
Break In Analysis
------------------
actual_password: 2290
observed_password: 9163
password_index: 1190
password_index_percent: 0.0011782178217821782
elapsed_time: 1h 21m
device_unlocked: False
```

### Classes

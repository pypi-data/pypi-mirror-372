import pytest
from typing_extensions import override

from shouldersurfscore.traditional_metrics import distances


class DistanceImpl(distances.Distance):
    """Dummy class that just returns the total length of both strings."""

    @override
    def distance(self, str1: str, str2: str) -> int:
        return len(str1) + len(str2)


def test_interface():
    impl = DistanceImpl()
    assert impl.name == "DistanceImpl"
    assert impl.distance("123", "abc") == 6


@pytest.mark.parametrize(
    "str1, str2, expected_distance",
    [
        # Basic cases
        ("kitten", "sitting", 3),  # Substitution, substitution, insertion
        ("saturday", "sunday", 3),  # Substitution, substitution, substitution
        ("flaw", "lawn", 2),  # Substitution, substitution
        # Identical strings
        ("abc", "abc", 0),
        # Empty strings
        ("", "", 0),
        ("abc", "", 3),
        ("", "abc", 3),
        # Single character differences
        ("a", "b", 1),
        ("a", "aa", 1),
        ("aa", "a", 1),
        ("a", "", 1),
        # Longer strings
        ("intention", "execution", 5),
        ("algorithm", "altruistic", 6),
        ("book", "back", 2),
        ("apple", "apply", 1),
        # Case sensitivity - The current implementation is case-sensitive.
        ("CAT", "cat", 3),
        ("hello", "HELLO", 5),
    ],
)
def test_levenshtein(str1: str, str2: str, expected_distance: int):
    lev = distances.Levenshtein()
    assert lev.name == "Levenshtein"
    assert lev.distance(str1, str2) == expected_distance

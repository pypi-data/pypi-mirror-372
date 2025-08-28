import abc

from typing_extensions import override


class Distance(abc.ABC):
    """
    An interface for calculating distances between two strings.

    Implementing classes need to define the following methods:<br>
    `def distance(self, str1: str, str2: str) -> int:`
    """

    @property
    def name(self) -> str:
        """The name of this instance's class."""
        return type(self).__name__

    @abc.abstractmethod
    def distance(self, str1: str, str2: str) -> int:
        """
        Abstract base method to implement computing the distance between two strings.

        Parameters
        ----------
        str1 : str
            The first string.
        str2 : str
            The second string.

        Returns
        -------
        int
            The distance between `str1` and `str2`.
        """


class Levenshtein(Distance):
    """
    Calculates the Levenshtein distance between two strings using dynamic programming.

    The algorithm creates a matrix where each element stores the
    distance between the first `i` characters of the first string and the first `j`
    characters of the second string.<br>
    The matrix is filled row by row.
    """

    @override
    def distance(self, str1: str, str2: str) -> int:
        m: int = len(str1)
        n: int = len(str2)

        # Create a 2D array (matrix) to store the distances
        # The size is (m+1) x (n+1) to handle empty prefixes
        dp: list[list[int]] = [[0] * (n + 1) for _ in range(m + 1)]

        # Initialize the first row and column
        # dp[i][0] = i (distance from str1[:i] to empty string)
        for i in range(m + 1):
            dp[i][0] = i
        # dp[0][j] = j (distance from empty string to str2[:j])
        for j in range(n + 1):
            dp[0][j] = j

        # Fill the rest of the matrix
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                # Cost is 0 if characters match, 1 otherwise
                cost: int = 0 if str1[i - 1] == str2[j - 1] else 1

                # The value of dp[i][j] is the minimum of three possibilities:
                dp[i][j] = min(
                    dp[i - 1][j] + 1,  # Deletion from str1
                    dp[i][j - 1] + 1,  # Insertion into str1
                    dp[i - 1][j - 1] + cost,  # Substitution (or match)
                )

        # The bottom-right cell contains the final distance
        return dp[m][n]

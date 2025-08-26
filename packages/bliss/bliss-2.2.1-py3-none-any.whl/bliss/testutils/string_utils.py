import re


class pytest_regex:
    r"""Pytest-like compare to check string matching.

    .. code-block::

        result = ["aaa", "10"]
        assert result == [pytest_regex(r"^[a-z]+$"), pytest_regex(r"^\d+$")]
    """

    def __init__(self, pattern: str, flags=0):
        self._compiled = re.compile(pattern, flags)

    def __eq__(self, actual) -> bool:
        return self._compiled.match(actual) is not None

    def __repr__(self) -> str:
        return self._compiled.pattern

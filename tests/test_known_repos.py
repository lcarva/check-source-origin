from __future__ import annotations

from check_source_origin.known_repos import lookup


class TestLookup:
    def test_exact_match(self) -> None:
        assert lookup("adlfs") == "https://github.com/fsspec/adlfs"

    def test_case_insensitive(self) -> None:
        assert lookup("ADLFS") == "https://github.com/fsspec/adlfs"

    def test_hyphen_underscore_normalization(self) -> None:
        result = lookup("some-package")
        assert result == lookup("some_package")

    def test_unknown_package(self) -> None:
        assert lookup("nonexistent-pkg-xyz") is None

from click.testing import CliRunner

from check_source_origin.cli import _print_diff_report, main
from check_source_origin.models import DiffReport, DiffResult, FileEntry


class TestPrintDiffReport:
    def _make_report(self) -> DiffReport:
        return DiffReport(
            added=[FileEntry(path="evil.py", digest="aaa")],
            removed=[
                FileEntry(path=".github/ci.yml", digest="bbb"),
                FileEntry(path="docs/index.rst", digest="ccc"),
            ],
            modified=[
                DiffResult(path="setup.py", sdist_digest="ddd", vcs_digest="eee")
            ],
            generated=[FileEntry(path="PKG-INFO", digest="fff")],
        )

    def test_default_shows_only_issues(self) -> None:
        report = self._make_report()
        output = _invoke_print(report, details=False)
        assert "FAIL" in output
        assert "Modified" in output
        assert "setup.py" in output
        assert "Unexpected" in output
        assert "evil.py" in output
        assert ".github/ci.yml" not in output
        assert "PKG-INFO" not in output

    def test_default_shows_hint(self) -> None:
        report = self._make_report()
        output = _invoke_print(report, details=False)
        assert "--details" in output
        assert "2 excluded" in output
        assert "1 generated" in output

    def test_no_hint_when_nothing_hidden(self) -> None:
        report = DiffReport(
            added=[FileEntry(path="evil.py", digest="aaa")],
            removed=[],
            modified=[],
            generated=[],
        )
        output = _invoke_print(report, details=False)
        assert "--details" not in output

    def test_details_shows_all_sections(self) -> None:
        report = self._make_report()
        output = _invoke_print(report, details=True)
        assert "FAIL" in output
        assert "setup.py" in output
        assert "evil.py" in output
        assert ".github/ci.yml" in output
        assert "PKG-INFO" in output

    def test_details_no_hint(self) -> None:
        report = self._make_report()
        output = _invoke_print(report, details=True)
        assert "--details" not in output

    def test_pass_no_issues(self) -> None:
        report = DiffReport(
            added=[],
            removed=[FileEntry(path=".github/ci.yml", digest="bbb")],
            modified=[],
            generated=[FileEntry(path="PKG-INFO", digest="fff")],
        )
        output = _invoke_print(report, details=False)
        assert "PASS" in output
        assert "Modified" not in output
        assert "Unexpected" not in output


def _invoke_print(report: DiffReport, details: bool) -> str:
    runner = CliRunner()
    import click

    @click.command()
    def _cmd() -> None:
        _print_diff_report(report, details=details)

    result = runner.invoke(_cmd, catch_exceptions=False)
    return result.output


class TestCLI:
    def test_help(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "Verify" in result.output

    def test_subcommands_listed(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert "resolve" in result.output
        assert "download" in result.output
        assert "diff" in result.output
        assert "verify" in result.output

    def test_resolve_help(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["resolve", "--help"])
        assert result.exit_code == 0
        assert "NAME" in result.output

    def test_diff_help(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["diff", "--help"])
        assert result.exit_code == 0
        assert "--repo" in result.output
        assert "--ref" in result.output

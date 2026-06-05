from click.testing import CliRunner

from check_source_origin.cli import main


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

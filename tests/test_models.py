import json

from check_source_origin.models import DiffReport, DiffResult, FileEntry, ResolveResult


class TestResolveResult:
    def test_creation(self) -> None:
        r = ResolveResult(
            repo_url="https://github.com/pallets/flask",
            commit="abc123",
            tag="3.0.0",
            resolution_method="attestation",
            verified=True,
        )
        assert r.repo_url == "https://github.com/pallets/flask"
        assert r.commit == "abc123"
        assert r.tag == "3.0.0"
        assert r.verified is True

    def test_to_dict(self) -> None:
        r = ResolveResult(
            repo_url="https://github.com/pallets/flask",
            commit="abc123",
            tag=None,
            resolution_method="pypi_metadata",
            verified=False,
        )
        d = r.to_dict()
        assert d["repo_url"] == "https://github.com/pallets/flask"
        assert d["tag"] is None
        assert d["verified"] is False
        json.dumps(d)


class TestDiffReport:
    def test_pass_when_no_diffs(self) -> None:
        report = DiffReport(
            added=[],
            removed=[],
            modified=[],
            generated=[FileEntry(path="PKG-INFO", digest="aaa")],
        )
        assert report.passed is True

    def test_fail_when_added(self) -> None:
        report = DiffReport(
            added=[FileEntry(path="evil.py", digest="bbb")],
            removed=[],
            modified=[],
            generated=[],
        )
        assert report.passed is False

    def test_fail_when_modified(self) -> None:
        report = DiffReport(
            added=[],
            removed=[],
            modified=[
                DiffResult(
                    path="setup.py",
                    sdist_digest="aaa",
                    vcs_digest="bbb",
                )
            ],
            generated=[],
        )
        assert report.passed is False

    def test_removed_only_still_passes(self) -> None:
        report = DiffReport(
            added=[],
            removed=[FileEntry(path=".github/ci.yml", digest="ccc")],
            modified=[],
            generated=[],
        )
        assert report.passed is True

    def test_to_dict(self) -> None:
        report = DiffReport(
            added=[FileEntry(path="x.py", digest="aaa")],
            removed=[],
            modified=[],
            generated=[],
        )
        d = report.to_dict()
        assert d["passed"] is False
        assert len(d["added"]) == 1
        json.dumps(d)

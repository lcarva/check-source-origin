import json
from pathlib import Path
from unittest.mock import patch

import httpx

from check_source_origin.depsdev import DepsDevClient

FIXTURES = Path(__file__).parent / "fixtures"


_FAKE_REQ = httpx.Request("GET", "https://fake")


def _mock_response(fixture_name: str) -> httpx.Response:
    data = (FIXTURES / fixture_name).read_text()
    return httpx.Response(200, json=json.loads(data), request=_FAKE_REQ)


def _mock_404() -> httpx.Response:
    return httpx.Response(404, json={"error": {"message": "not found"}}, request=_FAKE_REQ)


class TestDepsDevClient:
    def test_get_version_returns_parsed(self) -> None:
        with patch.object(httpx.Client, "get", return_value=_mock_response("depsdev_flask_3.1.1.json")):
            client = DepsDevClient()
            result = client.get_version("flask", "3.1.1")
        assert result["versionKey"]["name"] == "flask"
        assert result["versionKey"]["version"] == "3.1.1"

    def test_get_version_not_found_raises(self) -> None:
        with patch.object(httpx.Client, "get", return_value=_mock_404()):
            client = DepsDevClient()
            try:
                client.get_version("nonexistent", "0.0.0")
                assert False, "Should have raised"
            except Exception:
                pass

    def test_extract_attestations_with_verified(self) -> None:
        with patch.object(httpx.Client, "get", return_value=_mock_response("depsdev_flask_3.1.1.json")):
            client = DepsDevClient()
            data = client.get_version("flask", "3.1.1")
        attestations = DepsDevClient.extract_attestations(data)
        assert len(attestations) >= 1
        verified = [a for a in attestations if a["verified"]]
        assert len(verified) >= 1
        assert "github.com" in verified[0]["sourceRepository"]
        assert verified[0]["commit"] is not None

    def test_extract_attestations_empty(self) -> None:
        with patch.object(httpx.Client, "get", return_value=_mock_response("depsdev_requests_2.31.0.json")):
            client = DepsDevClient()
            data = client.get_version("requests", "2.31.0")
        attestations = DepsDevClient.extract_attestations(data)
        assert attestations == []

    def test_extract_related_projects(self) -> None:
        with patch.object(httpx.Client, "get", return_value=_mock_response("depsdev_requests_2.31.0.json")):
            client = DepsDevClient()
            data = client.get_version("requests", "2.31.0")
        projects = DepsDevClient.extract_related_projects(data)
        assert len(projects) >= 1
        assert any("github.com" in p["projectKey"]["id"] for p in projects)

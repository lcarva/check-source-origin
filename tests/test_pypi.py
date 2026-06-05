import json
from pathlib import Path
from unittest.mock import patch

import httpx

from check_source_origin.pypi import PyPIClient

FIXTURES = Path(__file__).parent / "fixtures"


_FAKE_REQ = httpx.Request("GET", "https://fake")


def _mock_response(fixture_name: str) -> httpx.Response:
    data = (FIXTURES / fixture_name).read_text()
    return httpx.Response(200, json=json.loads(data), request=_FAKE_REQ)


class TestPyPIClient:
    def test_get_version_metadata(self) -> None:
        with patch.object(httpx.Client, "get", return_value=_mock_response("pypi_flask_3.1.1.json")):
            client = PyPIClient()
            meta = client.get_version_metadata("flask", "3.1.1")
        assert meta["info"]["name"].lower() == "flask"

    def test_extract_sdist_url(self) -> None:
        with patch.object(httpx.Client, "get", return_value=_mock_response("pypi_flask_3.1.1.json")):
            client = PyPIClient()
            meta = client.get_version_metadata("flask", "3.1.1")
        sdist = PyPIClient.extract_sdist_info(meta)
        assert sdist is not None
        assert sdist["url"].endswith(".tar.gz")
        assert "sha256" in sdist["digests"]

    def test_extract_source_urls(self) -> None:
        with patch.object(httpx.Client, "get", return_value=_mock_response("pypi_flask_3.1.1.json")):
            client = PyPIClient()
            meta = client.get_version_metadata("flask", "3.1.1")
        urls = PyPIClient.extract_source_urls(meta)
        assert any("github.com" in u for u in urls)

    def test_extract_sdist_info_no_sdist(self) -> None:
        fake = {"urls": [{"packagetype": "bdist_wheel", "url": "x.whl", "digests": {}}]}
        sdist = PyPIClient.extract_sdist_info(fake)
        assert sdist is None

import hashlib
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import httpx

from check_source_origin.download import download_sdist
from check_source_origin.pypi import PyPIClient

FIXTURES = Path(__file__).parent / "fixtures"
_FAKE_REQ = httpx.Request("GET", "https://fake")


class TestDownloadSdist:
    def test_downloads_and_verifies_hash(self, tmp_path: Path) -> None:
        content = b"fake sdist tarball content"
        sha256 = hashlib.sha256(content).hexdigest()

        pypi_data = json.loads(
            (FIXTURES / "pypi_flask_3.1.1.json").read_text()
        )
        sdist_entry = PyPIClient.extract_sdist_info(pypi_data)
        assert sdist_entry is not None
        sdist_entry["digests"]["sha256"] = sha256

        output = tmp_path / "flask-3.1.1.tar.gz"

        mock_stream = MagicMock()
        mock_stream.__enter__ = MagicMock(return_value=mock_stream)
        mock_stream.__exit__ = MagicMock(return_value=False)
        mock_stream.iter_bytes = MagicMock(return_value=iter([content]))

        with patch.object(httpx.Client, "stream", return_value=mock_stream):
            result = download_sdist(
                url=sdist_entry["url"],
                expected_sha256=sha256,
                output=output,
            )

        assert result == output
        assert output.read_bytes() == content

    def test_raises_on_hash_mismatch(self, tmp_path: Path) -> None:
        content = b"tampered content"

        mock_stream = MagicMock()
        mock_stream.__enter__ = MagicMock(return_value=mock_stream)
        mock_stream.__exit__ = MagicMock(return_value=False)
        mock_stream.iter_bytes = MagicMock(return_value=iter([content]))

        output = tmp_path / "bad.tar.gz"

        with patch.object(httpx.Client, "stream", return_value=mock_stream):
            try:
                download_sdist(
                    url="https://files.pythonhosted.org/fake.tar.gz",
                    expected_sha256="0" * 64,
                    output=output,
                )
                assert False, "Should have raised"
            except ValueError as e:
                assert "hash mismatch" in str(e).lower()

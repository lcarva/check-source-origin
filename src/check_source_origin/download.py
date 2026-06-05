from __future__ import annotations

import hashlib
from pathlib import Path

import httpx


def download_sdist(
    url: str,
    expected_sha256: str,
    output: Path,
) -> Path:
    h = hashlib.sha256()
    client = httpx.Client(timeout=60, follow_redirects=True)

    with client.stream("GET", url) as resp:
        resp.raise_for_status()
        with open(output, "wb") as f:
            for chunk in resp.iter_bytes():
                f.write(chunk)
                h.update(chunk)

    actual = h.hexdigest()
    if actual != expected_sha256:
        output.unlink(missing_ok=True)
        raise ValueError(
            f"Hash mismatch for {url}: expected {expected_sha256}, got {actual}"
        )

    return output

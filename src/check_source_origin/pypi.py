from __future__ import annotations

import re
from typing import Any

import httpx

BASE_URL = "https://pypi.org"

_VCS_HOST_RE = re.compile(
    r"https?://(?:github\.com|gitlab\.com|bitbucket\.org)/[^/]+/[^/]+"
)


class PyPIClient:
    def __init__(self) -> None:
        self._client = httpx.Client(base_url=BASE_URL, timeout=30)

    def get_version_metadata(self, name: str, version: str) -> dict[str, Any]:
        resp = self._client.get(f"/pypi/{name}/{version}/json")
        resp.raise_for_status()
        return resp.json()  # type: ignore[no-any-return]

    @staticmethod
    def extract_sdist_info(data: dict[str, Any]) -> dict[str, Any] | None:
        for url_entry in data.get("urls", []):
            if url_entry.get("packagetype") == "sdist":
                return url_entry  # type: ignore[no-any-return]
        return None

    @staticmethod
    def extract_source_urls(data: dict[str, Any]) -> list[str]:
        urls: list[str] = []
        info = data.get("info", {})

        project_urls = info.get("project_urls") or {}
        for label, url in project_urls.items():
            if _VCS_HOST_RE.match(url):
                urls.append(url)

        home_page = info.get("home_page") or ""
        if _VCS_HOST_RE.match(home_page) and home_page not in urls:
            urls.append(home_page)

        return urls

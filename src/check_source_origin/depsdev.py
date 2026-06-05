from __future__ import annotations

from typing import Any

import httpx

BASE_URL = "https://api.deps.dev/v3alpha"


class DepsDevError(Exception):
    pass


class DepsDevClient:
    def __init__(self) -> None:
        self._client = httpx.Client(base_url=BASE_URL, timeout=30)

    def get_version(self, name: str, version: str) -> dict[str, Any]:
        resp = self._client.get(
            f"/systems/pypi/packages/{name}/versions/{version}"
        )
        if resp.status_code == 404:
            raise DepsDevError(f"Package {name}=={version} not found on deps.dev")
        resp.raise_for_status()
        return resp.json()  # type: ignore[no-any-return]

    @staticmethod
    def extract_attestations(data: dict[str, Any]) -> list[dict[str, Any]]:
        return data.get("attestations", [])  # type: ignore[no-any-return]

    @staticmethod
    def extract_related_projects(data: dict[str, Any]) -> list[dict[str, Any]]:
        return data.get("relatedProjects", [])  # type: ignore[no-any-return]

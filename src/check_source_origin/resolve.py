from __future__ import annotations

from .depsdev import DepsDevClient
from .models import ResolveResult
from .pypi import PyPIClient


class ResolveError(Exception):
    pass


def _repo_url_from_project_id(project_id: str) -> str:
    return f"https://{project_id}"


def resolve_source(name: str, version: str) -> ResolveResult:
    depsdev = DepsDevClient()
    pypi = PyPIClient()

    depsdev_data = depsdev.get_version(name, version)

    attestations = DepsDevClient.extract_attestations(depsdev_data)
    verified = [a for a in attestations if a.get("verified")]
    if verified:
        att = verified[0]
        return ResolveResult(
            repo_url=att["sourceRepository"],
            commit=att.get("commit"),
            tag=None,
            resolution_method="attestation",
            verified=True,
        )

    related = DepsDevClient.extract_related_projects(depsdev_data)
    source_repos = [
        p for p in related if p.get("relationType") == "SOURCE_REPO"
    ]
    if source_repos:
        project = source_repos[0]
        return ResolveResult(
            repo_url=_repo_url_from_project_id(project["projectKey"]["id"]),
            commit=None,
            tag=None,
            resolution_method="related_project",
            verified=False,
        )

    pypi_data = pypi.get_version_metadata(name, version)
    source_urls = PyPIClient.extract_source_urls(pypi_data)
    if source_urls:
        return ResolveResult(
            repo_url=source_urls[0],
            commit=None,
            tag=None,
            resolution_method="pypi_metadata",
            verified=False,
        )

    raise ResolveError(
        f"Could not resolve VCS source for {name}=={version}"
    )

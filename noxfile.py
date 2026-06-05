import nox

nox.options.default_venv_backend = "uv"


@nox.session(python=["3.10", "3.12"])
def tests(session: nox.Session) -> None:
    session.install("-e", ".[dev]", "pytest")
    session.run("pytest", *session.posargs)


@nox.session
def lint(session: nox.Session) -> None:
    session.install("ruff")
    session.run("ruff", "check", "src", "tests")


@nox.session
def typecheck(session: nox.Session) -> None:
    session.install("-e", ".", "mypy")
    session.run("mypy")

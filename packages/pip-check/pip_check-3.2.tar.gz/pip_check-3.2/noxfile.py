"""Basic tests around pip-check."""

from __future__ import annotations

import nox

nox.options.default_venv_backend = "uv"
nox.options.sessions = [
    "lint",
    "readme",
    "pip-check-test-py",
    "coverage",
]

python_versions = ["3.8", "3.9", "3.10", "3.11", "3.12", "3.13", "3.14"]


@nox.session(python=python_versions, name="pip-check-test-py")
def tests(session: nox.Session) -> None:
    """pip-check smoke tests."""
    session.install("--upgrade", "pip", "uv")
    session.install("html5lib==0.999999999", "django==1.10", "pyglet==2.0.dev23")
    session.install(".")

    response = session.run("pip-check", silent=True)

    # Make sure, packages are actually listed
    assert "1.10" in response
    assert "0.999999999" in response
    assert "2.0.dev23" in response

    session.run("pip-check", "--help")
    session.run("pip-check", "--version")
    session.run(
        "pip-check",
        "--ascii",
        "--not-required",
        "--full-version",
        "--hide-unchanged",
        "--show-update",
    )
    session.run("pip-check", "--user")
    session.run("pip-check", "--local")

    session.run("pip-check", "--cmd=uv pip")
    session.run("pip-check", "--cmd=uv pip", "--help")
    session.run(
        "pip-check", "--cmd=uv pip", "--ascii", "--full-version", "--hide-unchanged"
    )


@nox.session
def coverage(session: nox.Session) -> None:
    """Run the final coverage report."""
    session.install("--upgrade", "coverage")
    session.install("-e", ".")
    session.run("coverage", "erase")
    session.run("coverage", "run", "--append", "-m", "pip_check")
    session.run("coverage", "run", "--append", "-m", "pip_check", "--version")
    session.run(
        "coverage",
        "run",
        "--append",
        "-m",
        "pip_check",
        "--ascii",
        "--not-required",
        "--full-version",
        "--hide-unchanged",
        "--show-update",
    )
    session.run("coverage", "report")
    session.run("coverage", "html")


@nox.session
def readme(session: nox.Session) -> None:
    """Readme Validation."""
    session.install("markdown-it-py")
    session.run("markdown-it", "README.md", "/dev/null", external=True)


@nox.session
def lint(session: nox.Session) -> None:
    """Ruff codebase linting."""
    session.run("ruff", "check", "src", "noxfile.py", external=True)

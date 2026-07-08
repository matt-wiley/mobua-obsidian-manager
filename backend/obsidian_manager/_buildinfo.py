"""Build/version metadata, resolved once at import.

Version is git-tag driven (hatch-vcs). It comes from the installed package
metadata in a built wheel / Docker image, or from `git describe` in an editable
dev checkout. Commit and build date are baked as env vars at Docker build time
(git is not present in the runtime image), with a git fallback for dev.
"""

import functools
import os
import subprocess
from importlib import metadata
from pathlib import Path

_PKG_DIR = Path(__file__).parent


def _git(*args: str) -> str | None:
    try:
        out = subprocess.run(
            ["git", *args],
            capture_output=True,
            text=True,
            cwd=_PKG_DIR,
            timeout=2,
        )
        if out.returncode == 0:
            return out.stdout.strip() or None
    except Exception:
        pass
    return None


def _package_version() -> str | None:
    try:
        return metadata.version("obsidian-manager")
    except metadata.PackageNotFoundError:
        return None


@functools.lru_cache(maxsize=1)
def get_build_info() -> dict[str, str | None]:
    # Favor the live checkout so the badge reflects what is actually running,
    # including uncommitted changes (`-dirty`). Package metadata can be a stale
    # value baked by an earlier editable install, so it's only a fallback for
    # built/Docker installs where `.git` is absent.
    version = (
        os.environ.get("BUILD_VERSION")
        or _git("describe", "--tags", "--always", "--dirty")
        or _package_version()
        or "0+unknown"
    )
    # Normalize so the value is source-agnostic: git tags carry a leading "v"
    # (v0.1.0-…) but package metadata does not (0.1.0). The UI adds its own "v".
    version = version.removeprefix("v")

    commit = (
        os.environ.get("BUILD_COMMIT")
        or _git("rev-parse", "--short", "HEAD")
        or "unknown"
    )
    build_date = os.environ.get("BUILD_DATE") or _git("show", "-s", "--format=%cI", "HEAD")

    return {"version": version, "commit": commit, "build_date": build_date}

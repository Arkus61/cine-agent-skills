"""Build a deterministic archive from the repository's tracked files."""

from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path, PurePosixPath
import subprocess
import tempfile
import tomllib
import zipfile


ARCHIVE_TIMESTAMP = (1980, 1, 1, 0, 0, 0)
_FORBIDDEN_PARTS = {
    ".git",
    ".pytest_cache",
    ".superpowers",
    ".venv",
    ".worktrees",
    "__pycache__",
    "build",
    "dist",
}
_FORBIDDEN_SUFFIXES = (".pyc", ".pyo", ".zip")


def _forbidden_component(component: str) -> bool:
    lowered = component.lower()
    return component in _FORBIDDEN_PARTS or lowered.endswith((".egg-info", ".dist-info"))


def _tracked_paths(repository: Path) -> list[str]:
    # ``git archive`` produces a tracked-only snapshot without ``.git``. In
    # that case the snapshot itself is the authority; ignored setup output is
    # filtered by the same path rules before it can enter the archive.
    if not (repository / ".git").exists():
        paths: list[str] = []
        for candidate in repository.rglob("*"):
            if not candidate.is_file() or candidate.is_symlink():
                continue
            relative = candidate.relative_to(repository).as_posix()
            pure = PurePosixPath(relative)
            if any(_forbidden_component(part) for part in pure.parts):
                continue
            if relative.lower().endswith(_FORBIDDEN_SUFFIXES):
                continue
            paths.append(relative)
        return paths
    try:
        result = subprocess.run(
            ["git", "ls-files", "--cached", "-z"],
            cwd=repository,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        raise RuntimeError(f"unable to list tracked files: {exc}") from exc
    paths: list[str] = []
    for raw in result.stdout.split(b"\0"):
        if not raw:
            continue
        try:
            path = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError("tracked path is not valid UTF-8") from exc
        paths.append(path)
    return paths


def _validated_prefix(prefix: str) -> str:
    if not isinstance(prefix, str) or not prefix or "\\" in prefix:
        raise ValueError(f"unsafe archive prefix {prefix!r}")
    normalized = prefix.rstrip("/")
    pure = PurePosixPath(normalized)
    if (
        pure.is_absolute()
        or not normalized
        or any(part in {"", ".", ".."} for part in pure.parts)
        or any(_forbidden_component(part) for part in pure.parts)
    ):
        raise ValueError(f"unsafe archive prefix {prefix!r}")
    return normalized + "/"


def _validate_path(path: str, repository: Path) -> Path:
    pure = PurePosixPath(path)
    if (
        not path
        or "\\" in path
        or pure.is_absolute()
        or any(part in {"", ".", ".."} for part in pure.parts)
        or any(part in _FORBIDDEN_PARTS for part in pure.parts)
        or path.lower().endswith(_FORBIDDEN_SUFFIXES)
    ):
        raise ValueError(f"unsafe tracked path {path!r}")
    candidate = repository.joinpath(*pure.parts)
    try:
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(repository.resolve(strict=True))
    except (OSError, RuntimeError, ValueError) as exc:
        raise ValueError(f"unsafe tracked path {path!r}") from exc
    if candidate.is_symlink() or not candidate.is_file():
        raise ValueError(f"tracked path is not a regular file {path!r}")
    return candidate


def build_archive(
    repository: Path, output: Path, prefix: str = "cine-agent-skills/"
) -> str:
    """Build a stable ZIP and return its lowercase SHA-256 digest.

    Only files reported by ``git ls-files --cached`` are included. Paths and
    archive metadata are validated and ordered before the output is replaced.
    """

    root = Path(repository).resolve(strict=True)
    if not root.is_dir():
        raise ValueError(f"repository is not a directory: {repository}")
    archive_prefix = _validated_prefix(prefix)
    paths = sorted(set(_tracked_paths(root)))
    files = [(path, _validate_path(path, root)) for path in paths]

    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination_resolved = destination.resolve()
    for path, candidate in files:
        if candidate.resolve() == destination_resolved:
            raise ValueError(f"archive output is a tracked path {path!r}")

    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent, delete=False
        ) as temporary:
            temporary_name = temporary.name
        with zipfile.ZipFile(
            temporary_name,
            mode="w",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=9,
            strict_timestamps=True,
        ) as archive:
            for path, candidate in files:
                info = zipfile.ZipInfo(archive_prefix + path, date_time=ARCHIVE_TIMESTAMP)
                info.create_system = 3
                info.external_attr = (0o100644 << 16)
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info, candidate.read_bytes())
        os.replace(temporary_name, destination)
        temporary_name = None
    finally:
        if temporary_name:
            try:
                os.unlink(temporary_name)
            except FileNotFoundError:
                pass
    return hashlib.sha256(destination.read_bytes()).hexdigest()


def default_archive_output(repository: Path) -> Path:
    """Derive the archive name from the single package version source."""

    root = Path(repository)
    try:
        metadata = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
        version = metadata["project"]["version"]
    except (OSError, tomllib.TOMLDecodeError, KeyError, TypeError) as exc:
        raise ValueError(f"unable to read project.version: {exc}") from exc
    if not isinstance(version, str) or not version:
        raise ValueError("project.version must be a non-empty string")
    return Path("dist") / f"cine-agent-skills-{version}.zip"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
    )
    parser.add_argument("--prefix", default="cine-agent-skills/")
    args = parser.parse_args(argv)
    try:
        output = args.output if args.output is not None else default_archive_output(args.root)
        digest = build_archive(args.root, output, args.prefix)
    except (OSError, RuntimeError, ValueError) as exc:
        parser.error(str(exc))
    print(digest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

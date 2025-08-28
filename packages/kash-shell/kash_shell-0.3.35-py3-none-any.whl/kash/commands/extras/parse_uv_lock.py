from __future__ import annotations

import subprocess
import tomllib
from pathlib import Path
from typing import TYPE_CHECKING

from packaging.tags import Tag, sys_tags
from packaging.utils import parse_wheel_filename
from prettyfmt import fmt_size_dual
from strif import atomic_output_file

from kash.config.logger import get_logger
from kash.config.text_styles import COLOR_STATUS
from kash.exec import kash_command
from kash.shell.output.shell_output import cprint

if TYPE_CHECKING:
    from pandas import DataFrame

log = get_logger(__name__)


def choose_wheel(wheels: list[dict], allowed: list[Tag]) -> dict | None:
    """
    Pick the first wheel whose tag set intersects `allowed`
    (highest priority wins).
    """
    priority = {tag: idx for idx, tag in enumerate(allowed)}
    best: dict | None = None
    best_rank = float("inf")

    for meta in wheels:
        url = meta.get("url", "")
        filename = Path(url).name if url else ""
        if not filename:
            raise ValueError(f"No filename found for {url}")
        tags = parse_wheel_filename(filename)[-1]

        for tag in tags:
            rank = priority.get(tag)
            if rank is not None and rank < best_rank:
                best = meta
                best_rank = rank
                break

    return best


def get_platform() -> str:
    """
    Get the most-specific platform tag your interpreter supports.
    """
    return next(sys_tags()).platform


def parse_uv_lock(lock_path: Path) -> DataFrame:
    """
    Return one row per package from a uv.lock file, selecting the best
    matching wheel for the current interpreter or falling back to the sdist.

    Columns: name, version, registry, file_type, url, hash, size, filename.
    """
    from pandas import DataFrame

    with open(lock_path, "rb") as f:
        data = tomllib.load(f)

    rows: list[dict] = []
    for pkg in data.get("package", []):
        name = pkg.get("name")
        version = pkg.get("version")
        registry = pkg.get("source", {}).get("registry")

        wheels = pkg.get("wheels", [])
        selected = choose_wheel(wheels, list(sys_tags()))
        if selected:
            meta = selected
            file_type = "wheel"
        else:
            meta = pkg.get("sdist", {})
            file_type = "sdist"

        url = meta.get("url")
        rows.append(
            {
                "name": name,
                "version": version,
                "registry": registry,
                "file_type": file_type,
                "url": url,
                "hash": meta.get("hash"),
                "size": meta.get("size"),
                "filename": Path(url).name if url else None,
            }
        )

    return DataFrame(rows)


def uv_runtime_packages(
    project_dir: str | Path = ".", no_dev: bool = False, uv_executable: str = "uv"
) -> list[str]:
    """
    Return the *runtime* (non-dev) package names that would be installed for the
    given project, as resolved by uv.
    """
    cmd = [
        uv_executable,
        "export",
        "--format",
        "requirements-txt",
        "--no-header",
        "--no-annotate",
        "--no-hashes",
    ]
    if no_dev:
        cmd.append("--no-dev")

    result = subprocess.run(
        cmd,
        cwd=Path(project_dir),
        check=True,
        text=True,
        capture_output=True,
    )

    packages: list[str] = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if "==" not in line:  # skip “-e .” and blank lines
            continue
        pkg_name, _ = line.split("==", maxsplit=1)
        packages.append(pkg_name.strip())

    return packages


@kash_command
def uv_dep_info(
    uv_lock: str = "uv.lock",
    pyproject: str = "pyproject.toml",
    save: str | None = None,
    sort_by: str = "size",
) -> None:
    """
    Parse a uv.lock file and print information about the packages.
    By default, filters to show only 'main' dependencies from pyproject.toml.
    Helpful for looking at sizes of dependencies.
    """
    import pandas as pd

    uv_lock_path = Path(uv_lock)
    pyproject_path = Path(pyproject)

    main_deps: list[str] | None = None
    all_deps: list[str] = []
    if pyproject_path.exists():
        cprint("Reading main dependencies from with uv", style=COLOR_STATUS)
        main_deps = uv_runtime_packages(no_dev=True)
        all_deps = uv_runtime_packages(no_dev=False)
    else:
        log.warning("pyproject.toml not found: %s", pyproject_path)

    cprint(f"Parsing lock file: {uv_lock_path}", style=COLOR_STATUS)

    df = parse_uv_lock(uv_lock_path)
    df = df.sort_values(by=sort_by)

    if main_deps:
        cprint(
            f"Filtering lock file entries to include only {len(main_deps)} of {len(all_deps)} dependencies.",
            style=COLOR_STATUS,
        )
        df = df[df["name"].isin(main_deps)]
    else:
        cprint("Showing all packages from lock file.", style=COLOR_STATUS)
    cprint()

    # Show only selected columns and full output
    cols = ["name", "version", "file_type", "size", "filename"]
    print(df.loc[:, cols].to_string(max_rows=None))
    cprint()  # Add a newline for separation

    # Calculate and print summary stats
    num_deps = len(df)
    total_size = pd.Series(pd.to_numeric(df["size"], errors="coerce")).fillna(0).sum()

    cprint(f"Packages listed: {num_deps}", style=COLOR_STATUS)
    cprint(f"Total size: {fmt_size_dual(int(total_size))}", style=COLOR_STATUS)

    if save:
        with atomic_output_file(save) as temp_name:
            df.to_csv(temp_name, index=False)  # Added index=False for cleaner CSV
        cprint(f"Saved to {save}", style=COLOR_STATUS)

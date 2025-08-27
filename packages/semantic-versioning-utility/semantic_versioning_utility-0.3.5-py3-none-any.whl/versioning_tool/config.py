# python
from pathlib import Path


def find_proj_root(start_path=None):
    """Search upwards for a marker file to determine project root."""
    if start_path is None:
        start_path = Path.cwd()
    for parent in [start_path] + list(start_path.parents):
        if (parent / "pyproject.toml").exists() or (parent / "versioning.yaml").exists():
            return parent.resolve()
    raise FileNotFoundError("Project root not found.")


PROJ_ROOT = find_proj_root()
CHANGELOG_FILE = PROJ_ROOT / "CHANGELOG.md"
PYPROJECT_FILE = PROJ_ROOT / "pyproject.toml"
VERSIONING_CONFIG = PROJ_ROOT / "versioning.yaml"

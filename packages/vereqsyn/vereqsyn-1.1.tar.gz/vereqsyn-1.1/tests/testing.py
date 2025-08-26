import pathlib
import shutil


def tmp_copy(target: pathlib.Path, src: pathlib.Path) -> pathlib.Path:
    """Create a copy of ``src`` and return the new path."""
    shutil.copy(src, target)
    return target / src.name

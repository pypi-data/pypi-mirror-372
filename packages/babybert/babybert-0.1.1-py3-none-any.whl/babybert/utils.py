from __future__ import annotations

import importlib.resources
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from importlib.abc import Traversable


def resolve_checkpoint_path(name: str | Path) -> Path | Traversable:
    """
    Resolves a checkpoint name as either a local directory or a directory in the
    library.

    Prioritizes resolving the name with a local directory. If no local directory
    called `name` is discovered, then the function falls back to searching for a
    pretrained checkpoint in the library's `checkpoints/` directory.

    Args:
        name: The name to resolve. Can either be the name of a local directory of the
              name of a pretrained checkpoint included in the library.
    Returns:
        The resolved checkpoint path.
    """
    # If `name` is already a `Path`, simply return it.
    if isinstance(name, Path):
        return name

    # If `name` is the name of a local directory, return the path to the local
    # directory.
    if (local_dir := Path(name)).is_dir():
        return local_dir

    # Otherwise, search for the checkpoint in the library's `checkpoints/`
    # directory.
    checkpoints_dir = importlib.resources.files("babybert.checkpoints")

    if (checkpoint_dir := checkpoints_dir / name).is_dir():
        return checkpoint_dir

    available_checkpoints = ", ".join(dir.name for dir in checkpoints_dir.iterdir())

    raise FileNotFoundError(
        f"No checkpoint '{name}' was found locally or in the library's pretrained "
        f"checkpoints directory. Available checkpoints: {available_checkpoints}"
    )

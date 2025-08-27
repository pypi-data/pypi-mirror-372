"""
Notebook utility functions for reading, writing, validating, and manipulating notebook files and cells.
"""

import nbformat
from pathlib import Path
from jupyter_agent_toolkit.notebook.paths import ensure_allowed, ensure_allowed_for_write
import logging


def validate_notebook(nb: nbformat.NotebookNode) -> None:
    try:
        nbformat.validate(nb)
    except Exception as e:
        logging.error(f"Notebook validation failed: {e}")
        raise


def atomic_write_notebook(nb: nbformat.NotebookNode, path: Path) -> None:
    target = ensure_allowed_for_write(path)
    tmp = target.with_suffix(target.suffix + ".tmp")
    try:
        nbformat.write(nb, tmp)
        tmp.replace(target)
        logging.info(f"Notebook written atomically to {target}.")
    except Exception as e:
        logging.error(f"Failed to write notebook atomically to {target}: {e}")
        raise


def load_notebook(path: Path) -> nbformat.NotebookNode:
    p = ensure_allowed(path)
    try:
        nb = nbformat.read(p, as_version=4)
        logging.info(f"Notebook loaded from {p}.")
        return nb
    except Exception as e:
        logging.error(f"Failed to load notebook from {p}: {e}")
        raise


def save_notebook(nb: nbformat.NotebookNode, path: Path, validate: bool = True) -> None:
    # Convert outputs to NotebookNode objects for nbformat compatibility
    for cell in nb.get("cells", []):
        if cell.get("cell_type") == "code" and "outputs" in cell:
            cell["outputs"] = [nbformat.from_dict(out) if not isinstance(out, nbformat.NotebookNode) else out for out in cell["outputs"]]
    if validate:
        validate_notebook(nb)
    atomic_write_notebook(nb, path)

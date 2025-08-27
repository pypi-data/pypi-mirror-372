
from typing import Any, Dict, Optional
import logging

import nbformat
from nbformat import NotebookNode


def create_code_cell(
    source: Any,
    metadata: Optional[Dict[str, Any]] = None,
    outputs: Optional[Any] = None,
    execution_count: Optional[int] = None
) -> NotebookNode:
    """
    Create a new code cell using nbformat's schema-compliant helper.
    Accepts string or list for source.
    Args:
        source: The code for the cell (str or list of str).
        metadata: Optional metadata dict.
        outputs: Optional outputs list.
        execution_count: Optional execution count.
    Returns:
        NotebookNode: A new code cell.
    """
    if outputs is None:
        outputs = []

    return nbformat.v4.new_code_cell(
        source=source,
        metadata=metadata or {},
        outputs=outputs,
        execution_count=execution_count
    )


def create_markdown_cell(
    source: Any,
    metadata: Optional[Dict[str, Any]] = None
) -> NotebookNode:
    """
    Create a new markdown cell using nbformat's schema-compliant helper.
    Accepts string or list for source.
    Args:
        source: The markdown content (str or list of str).
        metadata: Optional metadata dict.
    Returns:
        NotebookNode: A new markdown cell.
    """
    return nbformat.v4.new_markdown_cell(
        source=source,
        metadata=metadata or {}
    )



def insert_cell(notebook: NotebookNode, cell: NotebookNode, index: int) -> None:
    """
    Insert a cell at a specific index. Raises IndexError if index is out of bounds.
    Logs the operation.
    """
    if not (0 <= index <= len(notebook.cells)):
        logging.error(f"insert_cell: Index {index} out of bounds for notebook with {len(notebook.cells)} cells.")
        raise IndexError(f"Index {index} out of bounds for notebook with {len(notebook.cells)} cells.")
    notebook.cells.insert(index, cell)
    logging.info(f"Inserted cell at index {index}.")



def append_cell(notebook: NotebookNode, cell: NotebookNode) -> None:
    """
    Append a cell to the end of the notebook. Logs the operation.
    """
    notebook.cells.append(cell)
    logging.info(f"Appended cell. Total cells: {len(notebook.cells)}.")



def remove_cell(notebook: NotebookNode, index: int) -> None:
    """
    Remove a cell at a specific index. Raises IndexError if index is out of bounds.
    Logs the operation.
    """
    if not (0 <= index < len(notebook.cells)):
        logging.error(f"remove_cell: Index {index} out of bounds for notebook with {len(notebook.cells)} cells.")
        raise IndexError(f"Index {index} out of bounds for notebook with {len(notebook.cells)} cells.")
    del notebook.cells[index]
    logging.info(f"Removed cell at index {index}.")



def get_cell(notebook: NotebookNode, index: int) -> NotebookNode:
    """
    Get a cell by index. Raises IndexError if index is out of bounds.
    """
    if not (0 <= index < len(notebook.cells)):
        logging.error(f"get_cell: Index {index} out of bounds for notebook with {len(notebook.cells)} cells.")
        raise IndexError(f"Index {index} out of bounds for notebook with {len(notebook.cells)} cells.")
    return notebook.cells[index]



def update_cell_source(notebook: NotebookNode, index: int, new_source: Any) -> None:
    """
    Update the source of a cell at a specific index. Accepts string or list for new_source.
    Raises IndexError if index is out of bounds. Logs the operation.
    """
    if not (0 <= index < len(notebook.cells)):
        logging.error(f"update_cell_source: Index {index} out of bounds for notebook with {len(notebook.cells)} cells.")
        raise IndexError(f"Index {index} out of bounds for notebook with {len(notebook.cells)} cells.")
    notebook.cells[index].source = new_source
    logging.info(f"Updated source of cell at index {index}.")



def update_cell_metadata(notebook: NotebookNode, index: int, new_metadata: Dict[str, Any]) -> None:
    """
    Update the metadata of a cell at a specific index. Raises IndexError if index is out of bounds. Logs the operation.
    """
    if not (0 <= index < len(notebook.cells)):
        logging.error(f"update_cell_metadata: Index {index} out of bounds for notebook with {len(notebook.cells)} cells.")
        raise IndexError(f"Index {index} out of bounds for notebook with {len(notebook.cells)} cells.")
    notebook.cells[index].metadata = new_metadata
    logging.info(f"Updated metadata of cell at index {index}.")

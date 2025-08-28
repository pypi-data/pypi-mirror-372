from collections.abc import Callable
from pathlib import Path


def read_items_from_file(path: Path, is_valid: Callable[[str], bool], lowercase: bool = False) -> list[str]:
    """Read items from a file and validate them.

    Raises:
        ValueError: if the file cannot be read or any item is invalid.
    """
    path = path.expanduser()
    if not path.is_file():
        raise ValueError(f"{path} is not a file")

    try:
        with path.open() as file:
            items = []
            for line_num, raw_line in enumerate(file, 1):
                item = raw_line.strip()
                if not item:  # Skip empty lines
                    continue

                if lowercase:
                    item = item.lower()

                if not is_valid(item):
                    raise ValueError(f"Invalid item in {path} at line {line_num}: {item}")
                items.append(item)

            return items
    except OSError as e:
        raise ValueError(f"Cannot read file {path}: {e}") from e


def read_lines_from_file(source: Path | str, lowercase: bool = False) -> list[str]:
    """Read non-empty lines from a file.

    Args:
        source: Path to the file to read from.
        lowercase: If True, convert all lines to lowercase.

    Returns:
        List of non-empty lines from the file.

    Raises:
        ValueError: if the file cannot be read or is not a file.
    """
    path = Path(source).expanduser()
    if not path.is_file():
        raise ValueError(f"{path} is not a file")

    try:
        with path.open() as file:
            lines = []
            for raw_line in file:
                stripped_line = raw_line.strip()
                if not stripped_line:  # Skip empty lines
                    continue

                if lowercase:
                    stripped_line = stripped_line.lower()

                lines.append(stripped_line)

            return lines
    except OSError as e:
        raise ValueError(f"Cannot read file {path}: {e}") from e

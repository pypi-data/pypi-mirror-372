from pathlib import Path


def convert_to_abs_path(file_path: str) -> Path:
    """
    Verify that the file exists and return the absolute path.

    Args:
        file_path: Absolute or relative path to the file to convert

    Returns:
        The absolute path to the file
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    return path.absolute()


import os
import shutil
import zipfile
from pathlib import Path

from fastapi import UploadFile
from loguru import logger


def create_init_file(folder: str | Path) -> Path | None:
    """
    Ensures that an __init__.py file exists in the given folder.

    Args:
        folder (str | Path): The folder in which to create __init__.py

    Returns:
        Path | None: The path to the __init__.py file, or None if creation failed or invalid input.
    """
    folder = Path(folder)
    init_file = folder / "__init__.py"

    if not folder.exists():
        logger.warning(f"Folder '{folder}' does not exist. Skipping __init__.py creation.")
        return None

    if not folder.is_dir():
        logger.warning(f"Path '{folder}' is not a directory. Skipping __init__.py creation.")
        return None

    if not init_file.exists():
        try:
            init_file.touch(exist_ok=True)
            logger.info(f"Created {init_file}")
        except Exception as e:
            logger.exception(f"Failed to create {init_file}: {e}")
            return None
    else:
        logger.debug(f"{init_file} already exists.")

    return init_file

def is_python_module(directory: Path) -> bool:
    return any(file.name == "__init__.py" or file.suffix == ".py" for file in directory.iterdir())


def extract_zip(file: UploadFile, target_folder):
    zip_path = os.path.join(target_folder, file.filename)
    with open(zip_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(target_folder)
    os.remove(zip_path)

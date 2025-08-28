import os
import contextlib
from loguru import logger

def read_content_of_file(file_full_name: str) -> str | None:
    """
    File reader with error handling. Emits warning (not error) if file not exists
    """
    if not os.path.exists(file_full_name):
        logger.warning(f"File {file_full_name} don't exists")
        return None
    try:
        with open(file_full_name, 'r', encoding="utf-8") as sf:
            content = sf.read()
        return content
    except Exception as e1:
        logger.error(f"File {file_full_name} cannot be opened, {e1}")
        return None


@contextlib.contextmanager
def open_with_missing_dirs(path, access_mode):
    """
    Open "path" for writing, creating any parent directories as needed.
    Similar to mkdir -p dir & edit file // path = dir + file
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, access_mode, encoding='utf-8') as file_handle:
        yield file_handle


def read_content_of_package_file(module_name: str, file_name: str) -> str:
    """
    Return content of one resource file included into named package. 
    Eg. core versioning scripts, module mappings, ...
    Subdir must have (empty) __init__.py file inside and so it can pointed as module (dot-notation).  
    And dirs/files must be built in during package build (edit pyproject.toml if problems arise).  
    File_name must be flat, no backslashes (must directly sit inside submodule) - up to 3.12
    Reads file with 'r' key (not 'rb'). Returns UTF-8 string
    """
    from importlib.resources import files # needs 3.7+, actually 3.9+
    
    try:
        # old way, deprecated in 3.11:        
        # with importlib.resources.open_text(module_name, file_name, encoding="UTF-8") as file:
        # new way, needs py 3.9, encoding="utf-8" is default (from 3.13 must used as kw-arg)
        with files(module_name).joinpath(file_name).open('r', encoding="utf-8") as handler: # 3.9+ (3.13+ allows multi pathnames)
            content = handler.read()
        return content # utf-8 string
    except Exception as e1:
        logger.error(f"Resource file {file_name} problem: {e1}")
        return ""


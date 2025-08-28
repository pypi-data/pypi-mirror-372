import logging
import os
import time
from datetime import datetime as dt
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict

log = logging.getLogger("util")


def date_str(dash: bool = False) -> str:
    """
    Return a date string. If dash is True, the date string will be in the format 'YYYY-MM-DD--HH-MM-SS'.
    If dash is False, the date string will be in the format 'YYYYMMDDHHMMSS'.

    Parameters
    ----------
    dash : bool
        Whether to include dashes in the date string. Default is False.

    Outputs
    -------
    str
        The date string.
    """
    if dash:
        return dt.now().strftime("%Y-%m-%d--%H-%M-%S")
    else:
        return dt.now().strftime("%Y%m%d%H%M%S")


def render_template(
    file: str, params_dict: Dict[str, Any], silent: bool = False
) -> str:
    """
    Read script and fill template params using params dict

    Parameters
    ----------
    file : str
        String to local file to template
    params_dict : dict
        Dictionary containg the keys/values for templating
    silent : bool
        Boolean indicating whether on not to log

    Outputs
    -------
    str
        String containing the formatted script
    """
    if not silent:
        log.info(f"Preparing {file}")
    with open(file) as f:
        return f.read().format(**params_dict)


def build_rel_path(*path_elements: str) -> Path:
    """
    Builds a path relative to the directory of the first file in path_elements using pathlib

    Parameters
    ----------
    *path_elements : str
        Variable number of str elements indicating the elements of the path to join together

    Outputs
    -------
    str
        String containing the relative path
    """
    initial_path = Path(path_elements[0])
    if initial_path.is_file():
        initial_path = initial_path.parent
    return str(initial_path.joinpath(*path_elements[1:]))


def load_env_var(name: str, default: str = None) -> str:
    """
    Load environment variable or return default

    Parameters
    ----------
    name : str
        Name of environment variable
    default : str
        Deafult value to return if environment variable not defined

    Outputs
    -------
    str
        Environment variable
    """
    return os.environ.get(name, default)


def validate_env_vars(vars: list) -> None:
    """
    Validate that all required environment variables are set

    Parameters
    ----------
    vars : list
        List of environment variables to check if exists
    """
    missing_vars = [var for var in vars if load_env_var(var) is None]
    if missing_vars:
        raise EnvironmentError(
            f"Missing environment variables: {', '.join(missing_vars)}"
        )


def timeit(func: Callable) -> Callable:
    """
    Decorator to measure time
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        log.info(f"{func.__name__} took {end_time - start_time:.4f} seconds")
        return result

    return wrapper

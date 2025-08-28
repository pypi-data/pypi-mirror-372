"""
Main module for reading maml files.
"""
import warnings
import os

import yaml

from .parse import is_valid

warnings.formatwarning = lambda msg, *args, **kwargs: f"{msg}\n"

def read_maml(file_name: str) -> dict:
    """
    Reads in a maml file and warns for strange extensions.
    """
    _, extension = os.path.splitext(file_name)
    match extension:
        case '.yml' | '.yaml':
            warnings.warn("WARNING: File read in but this is a .yml not a .maml\n")
        case '.maml':
            pass
        case _:
            warnings.warn("WARNING: Attempted to read in file but file missing correct extension.")
    with open(file_name, encoding='utf8') as file:
        maml_file = yaml.safe_load(file)
    if not is_valid(maml_file):
        warnings.warn(f"WARNING: {file_name} IS NOT VALID MAML\n")
    return maml_file

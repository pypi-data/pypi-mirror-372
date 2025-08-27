# import libs
from pathlib import Path
import yaml
# local


def load_yaml_file(filepath):
    """
    Safely load a YAML file and return its contents.

    Parameters
    ----------
    filepath : str or Path
        The path to the YAML file to be loaded.

    Returns
    -------
    dict
        The contents of the YAML file as a dictionary.
    """
    path = Path(filepath)
    if not path.is_file():
        raise FileNotFoundError(f"YAML file not found: {filepath}")
    with path.open('r', encoding='utf-8') as f:
        try:
            return yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Error parsing YAML file: {filepath}\n{e}")

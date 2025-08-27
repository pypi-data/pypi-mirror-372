from novus_pytils.files.core import get_files_by_extension
from novus_pytils.globals import TIFF_EXTS

def get_tiff_files(dir):
    """Get a list of TIFF image files in a folder.

    Args:
        dir (str): The path to the folder containing the TIFF image files.

    Returns:
        list: A list of TIFF image file paths.
    """
    return get_files_by_extension(dir, TIFF_EXTS)
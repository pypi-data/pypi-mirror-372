from novus_pytils.files.core import get_files_by_extension
from novus_pytils.globals import BMP_EXTS

def get_bmp_files(dir):
    """Get a list of BMP image files in a folder.

    Args:
        dir (str): The path to the folder containing the BMP image files.

    Returns:
        list: A list of BMP image file paths.
    """
    return get_files_by_extension(dir, BMP_EXTS)
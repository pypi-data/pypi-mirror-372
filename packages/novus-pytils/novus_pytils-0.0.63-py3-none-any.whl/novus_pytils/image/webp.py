from novus_pytils.files.core import get_files_by_extension
from novus_pytils.globals import WEBP_EXTS

def get_webp_files(dir):
    """Get a list of WEBP image files in a folder.

    Args:
        dir (str): The path to the folder containing the WEBP image files.

    Returns:
        list: A list of WEBP image file paths.
    """
    return get_files_by_extension(dir, WEBP_EXTS)
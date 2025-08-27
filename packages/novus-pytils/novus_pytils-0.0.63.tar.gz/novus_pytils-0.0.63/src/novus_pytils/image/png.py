from novus_pytils.files.core import get_files_by_extension
from novus_pytils.globals import PNG_EXTS

def get_png_files(dir):
    """Get a list of PNG image files in a folder.

    Args:
        dir (str): The path to the folder containing the PNG image files.

    Returns:
        list: A list of PNG image file paths.
    """
    return get_files_by_extension(dir, PNG_EXTS)
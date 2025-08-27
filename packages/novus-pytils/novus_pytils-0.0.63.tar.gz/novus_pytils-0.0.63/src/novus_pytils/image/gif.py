from novus_pytils.files.core import get_files_by_extension
from novus_pytils.globals import GIF_EXTS

def get_gif_files(dir):
    """Get a list of GIF image files in a folder.

    Args:
        dir (str): The path to the folder containing the GIF image files.

    Returns:
        list: A list of GIF image file paths.
    """
    return get_files_by_extension(dir, GIF_EXTS)
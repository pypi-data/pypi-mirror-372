from novus_pytils.files.core import get_files_by_extension
from novus_pytils.globals import JPG_EXTS

def get_jpg_files(dir):
    """Get a list of JPG/JPEG image files in a folder.

    Args:
        dir (str): The path to the folder containing the JPG/JPEG image files.

    Returns:
        list: A list of JPG/JPEG image file paths.
    """
    return get_files_by_extension(dir, JPG_EXTS)
from pydub import AudioSegment
from novus_pytils.files.core import get_files_by_extension
from novus_pytils.globals import AAC_EXTS

def get_aac_files(dir):
    """Get a list of AAC audio files in a folder.

    Args:
        dir (str): The path to the folder containing the AAC audio files.

    Returns:
        list: A list of AAC audio file paths.
    """
    return get_files_by_extension(dir, AAC_EXTS)

def is_aac_file(file):
    """Check if a file is an AAC audio file.

    Args:
        file (str): The path to the file to check.

    Returns:
        bool: True if the file is an AAC audio file, False otherwise.
    """
    return any(file.lower().endswith(ext) for ext in AAC_EXTS)

def filter_aac_files(files):
    """Filter a list of files to include only AAC audio files.

    Args:
        files (list): A list of file paths to filter.

    Returns:
        list: A list of AAC audio file paths.
    """
    return [file for file in files if is_aac_file(file)]

def count_aac_files(dir):
    """Count the number of AAC audio files in a folder.

    Args:
        dir (str): The path to the folder containing the AAC audio files.

    Returns:
        int: The number of AAC audio files in the folder.
    """
    return len(get_aac_files(dir))

def has_aac_files(dir):
    """Check if a folder contains any AAC audio files.

    Args:
        dir (str): The path to the folder to check.

    Returns:
        bool: True if the folder contains any AAC audio files, False otherwise.
    """
    return count_aac_files(dir) > 0

def aac_to_wav(aac_file, wav_file, bitrate=None, channels=None):
    """Convert an AAC audio file to WAV format.

    Args:
        aac_file (str): The path to the AAC audio file.
        wav_file (str): The path to save the converted WAV audio file.
        bitrate (str): The bitrate for the output file (not applicable for WAV).
        channels (int): The number of channels for the output file.

    Returns:
        None
    """
    audio = AudioSegment.from_file(aac_file, format="aac")
    if channels:
        audio = audio.set_channels(channels)
    audio.export(wav_file, format="wav")
    
def aac_to_mp3(aac_file, mp3_file, bitrate="192k", channels=None):
    """Convert an AAC audio file to MP3 format.

    Args:
        aac_file (str): The path to the AAC audio file.
        mp3_file (str): The path to save the converted MP3 audio file.
        bitrate (str): The bitrate for the output MP3 file (default is "192k").
        channels (int): The number of channels for the output file.

    Returns:
        None
    """
    audio = AudioSegment.from_file(aac_file, format="aac")
    if channels:
        audio = audio.set_channels(channels)
    audio.export(mp3_file, format="mp3", bitrate=bitrate)
    
def aac_to_m4a(aac_file, m4a_file, bitrate="192k", channels=None):
    """Convert an AAC audio file to M4A format.

    Args:
        aac_file (str): The path to the AAC audio file.
        m4a_file (str): The path to save the converted M4A audio file.
        bitrate (str): The bitrate for the output M4A file (default is "192k").
        channels (int): The number of channels for the output file.

    Returns:
        None
    """
    audio = AudioSegment.from_file(aac_file, format="aac")
    if channels:
        audio = audio.set_channels(channels)
    audio.export(m4a_file, format="ipod", bitrate=bitrate)
    
def aac_to_flac(aac_file, flac_file, bitrate=None, channels=None):
    """Convert an AAC audio file to FLAC format.

    Args:
        aac_file (str): The path to the AAC audio file.
        flac_file (str): The path to save the converted FLAC audio file.
        bitrate (str): The bitrate for the output file (not applicable for FLAC).
        channels (int): The number of channels for the output file.

    Returns:
        None
    """
    audio = AudioSegment.from_file(aac_file, format="aac")
    if channels:
        audio = audio.set_channels(channels)
    audio.export(flac_file, format="flac")
    
def aac_to_wma(aac_file, wma_file, bitrate="192k", channels=None):
    """Convert an AAC audio file to WMA format.

    Args:
        aac_file (str): The path to the AAC audio file.
        wma_file (str): The path to save the converted WMA audio file.
        bitrate (str): The bitrate for the output WMA file (default is "192k").
        channels (int): The number of channels for the output file.

    Returns:
        None
    """
    audio = AudioSegment.from_file(aac_file, format="aac")
    if channels:
        audio = audio.set_channels(channels)
    audio.export(wma_file, format="wma", bitrate=bitrate)
    
def aac_to_ogg(aac_file, ogg_file, bitrate="192k", channels=None):
    """Convert an AAC audio file to OGG format.

    Args:
        aac_file (str): The path to the AAC audio file.
        ogg_file (str): The path to save the converted OGG audio file.
        bitrate (str): The bitrate for the output OGG file (default is "192k").
        channels (int): The number of channels for the output file.

    Returns:
        None
    """
    audio = AudioSegment.from_file(aac_file, format="aac")
    if channels:
        audio = audio.set_channels(channels)
    audio.export(ogg_file, format="ogg", bitrate=bitrate)
    
def aac_to_aac(aac_file, aac_file_out, bitrate="192k", channels=None):
    """Convert an AAC audio file to another AAC audio file with specified bitrate.

    Args:
        aac_file (str): The path to the input AAC audio file.
        aac_file_out (str): The path to the output AAC audio file.
        bitrate (str): The bitrate for the output AAC file (default is "192k").
        channels (int): The number of channels for the output file.

    Returns:
        None
    """
    audio = AudioSegment.from_file(aac_file, format="aac")
    if channels:
        audio = audio.set_channels(channels)
    audio.export(aac_file_out, format="aac", bitrate=bitrate)
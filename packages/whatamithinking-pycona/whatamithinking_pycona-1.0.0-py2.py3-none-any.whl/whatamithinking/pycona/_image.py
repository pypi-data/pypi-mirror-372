from pathlib import Path
import shutil


class Image:
    """Pillow Image interface, to avoid Pillow dependency."""

    def __init__(self, ico_filepath: Path = None, png_filepath: Path = None) -> None:
        self.ico_filepath = ico_filepath
        self.png_filepath = png_filepath

    def save(self, file, format):
        format = format.lower().strip()
        if format == 'png':
            filepath = self.png_filepath
        elif format == 'ico':
            filepath = self.ico_filepath
        else:
            raise ValueError(f"File format, {format}, not supported.")
        if filepath is None:
            raise ValueError(f"Filepath is null for image format, {format}.")
        with open(filepath, 'rb') as image:
            shutil.copyfileobj(image, file)

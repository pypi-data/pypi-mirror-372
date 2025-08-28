from pathlib import Path

from loguru import logger


class JZMedia:
    """Class to handle media-related functionality."""
    def __init__(self):
        self._media_path = None

    def set_media_folder(self, folder: str) -> bool:
        """Set the media folder path, ensuring it exists and is writable."""
        absolute_path = Path(folder)
        old_media_path = self._media_path

        err = (
            f"The app has no permission to write to provided media folder {folder}. "
            "Media won't be saved."
        )
        err2 = f"Failed to create media folder {folder}. Media won't be saved."
        err3 = f"Failed to access provided media folder {folder}. Media won't be saved."

        # Ensure folder exists
        if not absolute_path.exists():
            logger.warning(f"Provided media folder does not exist: {absolute_path}")
            logger.warning("Attempting to create media folder...")
            try:
                absolute_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"New media folder created successfully @ {absolute_path}")
            except PermissionError:
                logger.error(err)
                self._media_path = old_media_path
                return False
            except Exception:
                logger.error(f"Failed to create media folder: {err2}")
                self._media_path = old_media_path
                return False

        # Check write permission
        try:
            test_file = absolute_path / "test.txt"
            with test_file.open(mode='w') as f:
                f.write("TEST")
            test_file.unlink()
            self._media_path = absolute_path
            logger.info(f"Media folder set successfully @ {self._media_path}")
        except PermissionError:
            logger.error(err)
            self._media_path = old_media_path
            return False
        except Exception:
            logger.error(f"Failed to write to media folder: {err3}")
            self._media_path = old_media_path
            return False
        else:
            return True

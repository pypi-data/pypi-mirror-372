import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class LanguageDetector:
    """Base class for language detectors. Subclasses should define `detection_files`."""

    detection_files: list[str] = []

    def __init__(self):
        # This check prevents direct instantiation of the base class, making it effectively abstract.
        if type(self) is LanguageDetector:
            raise TypeError(
                "LanguageDetector is an abstract base class and cannot be instantiated directly."
            )

    def detect(self, project_path: Path) -> bool:
        """
        Detect if this language is present by checking for specific files.

        Returns:
            bool: True if language is detected, False otherwise.
        """
        if not self.detection_files:
            logger.warning(f"Detector {self.__class__.__name__} has no detection_files defined.")
            return False

        try:
            return any((project_path / file).exists() for file in self.detection_files)
        except Exception as e:
            logger.error(f"Error during detection for {self.__class__.__name__} in {project_path}: {e}")
            return False
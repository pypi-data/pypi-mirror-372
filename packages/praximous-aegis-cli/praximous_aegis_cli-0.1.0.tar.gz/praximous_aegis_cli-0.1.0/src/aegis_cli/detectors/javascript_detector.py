from .base_detector import LanguageDetector
from pathlib import Path

class JavaScriptDetector(LanguageDetector):
    """Detects JavaScript projects by looking for common package management files."""
    detection_files = [
        'package.json',
        'yarn.lock',
        'package-lock.json',
    ]
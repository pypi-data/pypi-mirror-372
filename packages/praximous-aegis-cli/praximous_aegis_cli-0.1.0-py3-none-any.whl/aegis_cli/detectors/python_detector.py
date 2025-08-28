import logging
from .base_detector import LanguageDetector
from pathlib import Path

logger = logging.getLogger(__name__)

class PythonDetector(LanguageDetector):
    detection_files = [
        'requirements.txt',
        'pyproject.toml',
        'setup.py',
        'Pipfile',
        'poetry.lock',
        'setup.cfg'
    ]
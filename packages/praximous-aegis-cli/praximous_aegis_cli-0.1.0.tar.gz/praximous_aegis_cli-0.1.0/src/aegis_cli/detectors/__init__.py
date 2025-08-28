from pathlib import Path
from .python_detector import PythonDetector
from .javascript_detector import JavaScriptDetector

def detect_language(project_path: Path, verbose: bool = False) -> str:
    detectors = [
        ('javascript', JavaScriptDetector()),
        ('python', PythonDetector())
    ]
    
    for lang_name, detector in detectors:
        if detector.detect(project_path):
            if verbose:
                print(f"Detected {lang_name} project")
            return lang_name
    
    return None
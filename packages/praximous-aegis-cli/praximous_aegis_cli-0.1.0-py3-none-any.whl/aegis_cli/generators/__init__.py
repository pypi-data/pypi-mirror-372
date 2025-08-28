import logging
from pathlib import Path

import click
from .helpers import generate_from_template

logger = logging.getLogger(__name__)

def get_package_ecosystem(language: str) -> str | None:
    """Maps a language to a GitHub Dependabot package ecosystem."""
    ecosystems = {
        "python": "pip",
        "javascript": "npm",
    }
    return ecosystems.get(language.lower())

def generate_security_files(project_path: Path, output_dir: Path, language: str, verbose: bool = False) -> bool:
    """Generate all security files"""
    if verbose:
        click.echo(f"Generating files in: {output_dir}")

    # Define all files to be generated
    generators = [
        {
            "template": "SECURITY.md.j2",
            "output_path": output_dir / "SECURITY.md",
            "context": {"language": language, "project_name": project_path.name or "Our Project"},
        },
        {
            "template": "SecureCodingGuide.md.j2",
            "output_path": output_dir / "SecureCodingGuide.md",
            "context": {"language": language},
        },
        {
            "template": "dependabot.yml.j2",
            "output_path": project_path / ".github" / "dependabot.yml",
            "context": {"package_ecosystem": get_package_ecosystem(language)},
            "skip_if_context_missing": "package_ecosystem",
        },
    ]

    results = []
    for config in generators:
        if config.get("skip_if_context_missing") and not config["context"].get(config["skip_if_context_missing"]):
            logger.info(f"Skipping {config['template']} due to missing context.")
            continue
        results.append(generate_from_template(config["template"], config["output_path"], config["context"]))

    return all(results)
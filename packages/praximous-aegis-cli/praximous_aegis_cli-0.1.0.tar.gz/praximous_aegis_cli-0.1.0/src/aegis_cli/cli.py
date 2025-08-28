import click
import os
import logging
from pathlib import Path
from .detectors import detect_language
from .generators import generate_security_files

# Configure logging
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

@click.command()
@click.argument('project_path', type=click.Path(exists=True), default='.')
@click.option('--output', '-o', type=click.Path(), help='Custom output directory')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.option('--dry-run', is_flag=True, help='Show what would be generated without writing files')
def cli(project_path, output, verbose, dry_run):
    """Automate security documentation for your project"""

    try:
        project_path = Path(project_path).resolve()
        output_dir = Path(output) if output else project_path / 'security'

        if verbose:
            click.echo(f"Scanning project: {project_path}")
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)

        # Detect language
        try:
            language = detect_language(project_path, verbose)
        except Exception as e:
            logger.error(f"Error detecting language: {e}")
            raise click.ClickException("Error detecting project language.")

        if not language:
            logger.warning("No supported language detected.")
            # Use ClickException for controlled exit with error message and code 1
            raise click.ClickException("Could not detect supported language (Python/JavaScript)")

        if verbose:
            click.echo(f"Detected language: {language}")
            logger.debug(f"Detected language: {language}")

        # Generate files
        if dry_run:
            click.echo("📝 Dry run - would generate:")
            click.echo(f"  - SECURITY.md (in {output_dir})")
            click.echo(f"  - SecureCodingGuide.md (in {output_dir})")
            click.echo(f"  - dependabot.yml (in {project_path / '.github'})")
            click.echo(f"Total: 3 security files")
            logger.info("Dry run completed.")
        else:
            try:
                success = generate_security_files(project_path, output_dir, language, verbose)
            except Exception as e:
                logger.error(f"Error generating security files: {e}")
                raise click.ClickException("Failed to generate security files due to an error.")

            if success:
                click.echo("✅ Security files generated successfully!")
                click.echo(f"📁 SECURITY.md & SecureCodingGuide.md → {output_dir}")
                click.echo(f"📁 dependabot.yml → {project_path / '.github'}")
                logger.info("Security files generated successfully.")
            else:
                logger.error("Security file generation failed.")
                raise click.ClickException("Failed to generate one or more security files. Check logs.")

    except Exception as e:
        logger.critical(f"Unhandled exception: {e}", exc_info=True)
        if not isinstance(e, click.ClickException):
            raise click.ClickException(f"An unexpected error occurred: {e}")
        raise # Re-raise the ClickException

if __name__ == '__main__':
    cli()
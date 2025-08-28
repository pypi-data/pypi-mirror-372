from pathlib import Path
import jinja2
import logging
try:
    from importlib import resources
except ImportError:
    # Python 3.8 compatibility
    import importlib_resources as resources

logger = logging.getLogger(__name__)

def generate_from_template(template_name: str, output_path: Path, context: dict) -> bool:
    """
    Generates a file from a Jinja2 template.

    Args:
        template_name: The name of the template file in the 'templates' directory.
        output_path: The full path where the generated file will be saved.
        context: A dictionary of context variables to pass to the template.

    Returns:
        True if the file was generated successfully, False otherwise.
    """
    try:
        # Use importlib.resources for reliable template access across Python versions
        template_content = resources.files('aegis_cli.templates').joinpath(template_name).read_text(encoding='utf-8')

        template = jinja2.Template(template_content, undefined=jinja2.StrictUndefined)
        content = template.render(**context)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding='utf-8')
        return True
    except Exception as e:
        logger.error(f"Failed to generate {output_path.name} from {template_name}: {e}", exc_info=True)
        return False
import os
import jinja2
import logging
from pathlib import Path
from typing import Optional


def render_template(filename: Path, kwargs) -> Optional[str]:
    """Use Jinja2 to render kwargs into filename and return result as string."""
    searchpath = os.path.dirname(filename)
    loader = jinja2.FileSystemLoader(searchpath=searchpath)
    env = jinja2.Environment(loader=loader, trim_blocks=True, lstrip_blocks=True)
    template = env.get_template(os.path.basename(filename))
    result = template.render(**kwargs)
    if isinstance(result, str):
        return result
    else:
        msg = f"Failed to render template {filename}."
        logging.critical(msg)
        return None


def render_template_from_templates(filename: Path, kwargs) -> Optional[str]:
    """Render kwargs into file in templates directory that comes with iTCHi."""
    assert filename == Path(os.path.basename(filename))
    # The location where render.py (aka __file__) is located is where the other
    # templates are, too.
    templates_path = os.path.abspath(os.path.dirname(__file__))
    return render_template(Path(os.path.join(templates_path, filename)), kwargs)


def render_string(input: str, **kwargs) -> Optional[str]:
    template = jinja2.Template(input)
    result = template.render(**kwargs)
    return result

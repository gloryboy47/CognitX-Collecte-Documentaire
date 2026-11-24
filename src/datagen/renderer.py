"""Rendu des templates Jinja2 en PDF via WeasyPrint."""

from __future__ import annotations

from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

TEMPLATES_DIR = Path(__file__).parent / "templates"

_env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=False,
)


def render_html(template_name: str, data: dict) -> str:
    tpl = _env.get_template(template_name)
    return tpl.render(**data)


def html_to_pdf(html_content: str, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    HTML(string=html_content).write_pdf(str(output_path))
    return output_path


def generate_pdf(template_name: str, data: dict, output_path: Path) -> Path:
    html = render_html(template_name, data)
    return html_to_pdf(html, output_path)

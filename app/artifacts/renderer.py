"""WorkoutPlan JSON → Jinja2 HTML → WeasyPrint PDF. Deterministic, agent-free."""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML

_TEMPLATES = Path(__file__).parent / "templates"
_env = Environment(
    loader=FileSystemLoader(_TEMPLATES),
    autoescape=select_autoescape(["html"]),
)


def render_program_pdf(plan: dict, created_at: str | None = None) -> bytes:
    html = _env.get_template("program.html").render(plan=plan, created_at=created_at)
    return HTML(string=html, base_url=str(_TEMPLATES)).write_pdf()

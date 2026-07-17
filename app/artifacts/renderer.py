"""WorkoutPlan JSON → Jinja2 HTML → WeasyPrint PDF. Deterministic, agent-free."""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML

from app.exercises.resolver import media_for

_TEMPLATES = Path(__file__).parent / "templates"
_env = Environment(
    loader=FileSystemLoader(_TEMPLATES),
    autoescape=select_autoescape(["html"]),
)


def render_program_pdf(plan: dict, created_at: str | None = None) -> bytes:
    # Start/end form frames per exercise (None entries render without images).
    media = {}
    for day in plan.get("weekly_split", []):
        for ex in day.get("exercises", []):
            name = ex.get("exercise", "")
            if name not in media:
                media[name] = media_for(name)
    media = {k: v for k, v in media.items() if v}

    html = _env.get_template("program.html").render(
        plan=plan, created_at=created_at, media=media, media_credits=bool(media)
    )
    return HTML(string=html, base_url=str(_TEMPLATES)).write_pdf()

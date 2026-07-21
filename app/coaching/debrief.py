"""Post-session debriefs + weekly review summaries (deterministic, fast)."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any


def session_debrief(
    day_label: str,
    exercises: list[dict],
    load: dict | None,
    prs: list[str],
    adaptation: dict | None,
) -> dict[str, Any]:
    total_sets = sum(len(ex.get("logged_sets") or []) for ex in exercises)
    planned = sum(int(ex.get("sets") or 0) for ex in exercises)
    completion = round(100 * total_sets / planned) if planned else 0

    lines: list[str] = []
    lines.append(f"**{day_label}** — session locked.")
    if prs:
        lines.append("PRs today: " + ", ".join(prs) + ". That's real progress — own it.")
    if completion >= 100:
        lines.append("Full plan completed. Recovery is the next training session.")
    elif completion >= 70:
        lines.append(f"Solid body of work ({completion}% of planned sets). Enough stimulus.")
    else:
        lines.append(
            f"Partial session ({completion}% of planned sets). We'll adjust — showing up still counts."
        )

    acwr = (load or {}).get("acwr")
    if isinstance(acwr, (int, float)):
        if acwr > 1.5:
            lines.append(f"Load spike watch: ACWR {acwr}. Bias recovery tomorrow.")
        elif acwr < 0.8:
            lines.append(f"ACWR {acwr} is low — room to push denser work this week if joints feel good.")
        else:
            lines.append(f"ACWR {acwr} — in a productive zone.")

    if adaptation and adaptation.get("soft_day"):
        lines.append("Today was already recovery-biased. Sleep and protein still matter tonight.")

    next_cue = "Next session: same standards — warm up, hit the plan, leave notes if anything hurts."
    if prs:
        next_cue = "Next session: don't chase yesterday's PRs early — earn them again with clean reps."
    lines.append(next_cue)

    return {
        "headline": "Day complete — nice work." if completion >= 70 else "Session logged.",
        "completion_pct": completion,
        "prs": prs,
        "message": "\n\n".join(lines),
        "next_cue": next_cue,
    }


def weekly_review_payload(
    profile: dict,
    readiness: list[dict],
    load: dict,
    recent_workouts: list[dict],
    pr_names: list[str],
) -> dict[str, Any]:
    sessions = load.get("sessions_28d") or len(recent_workouts)
    acwr = load.get("acwr")
    goal = profile.get("goals") or profile.get("goal_mode") or "general progress"

    wins: list[str] = []
    focuses: list[str] = []

    if pr_names:
        wins.append("PRs this stretch: " + ", ".join(sorted(set(pr_names))[:6]))
    if sessions:
        wins.append(f"{sessions} sessions logged in the last 28 days.")
    if readiness:
        sleeps = [r["sleep_h"] for r in readiness if isinstance(r.get("sleep_h"), (int, float))]
        if sleeps:
            avg = sum(sleeps) / len(sleeps)
            wins.append(f"Avg sleep (recent): {avg:.1f}h.")
            if avg < 6.5:
                focuses.append("Protect a 7–8h sleep window — training quality tracks sleep.")

    if isinstance(acwr, (int, float)):
        if acwr > 1.5:
            focuses.append(f"ACWR {acwr}: schedule a lighter week before stacking intensity.")
        elif acwr < 0.8:
            focuses.append(f"ACWR {acwr}: you can densify volume if recovery is clean.")
        else:
            wins.append(f"ACWR {acwr} is in a productive zone.")

    bw = profile.get("bodyweight_lbs")
    nutrition = profile.get("nutrition_targets") or {}
    if bw and nutrition.get("protein_g"):
        focuses.append(
            f"Nutrition anchor: ~{nutrition['protein_g']}g protein/day at {bw} lbs bodyweight."
        )
    elif bw:
        focuses.append(f"Hit ~{round(float(bw) * 0.8)}–{round(float(bw))}g protein/day as a baseline.")

    if not focuses:
        focuses.append(f"Stay consistent on the plan aimed at: {goal}.")

    message = (
        f"**Weekly review — Coach K**\n\n"
        f"Goal lens: {goal}\n\n"
        f"**Wins**\n" + ("\n".join(f"• {w}" for w in wins) or "• Building the baseline — keep logging.")
        + "\n\n**Next week focus**\n"
        + "\n".join(f"• {f}" for f in focuses)
    )
    return {
        "title": "Coach K — weekly review",
        "wins": wins,
        "focuses": focuses,
        "message": message,
        "week_of": str(date.today() - timedelta(days=date.today().weekday())),
    }

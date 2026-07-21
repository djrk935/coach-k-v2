/**
 * Share helpers — Web Share API with clipboard fallback.
 * Plain text only (no auth keys in shared content).
 */

export type Shareable = { title: string; text: string };

export async function shareContent(payload: Shareable): Promise<"shared" | "copied" | "failed"> {
  const data = { title: payload.title, text: payload.text };
  try {
    if (typeof navigator !== "undefined" && typeof navigator.share === "function") {
      await navigator.share(data);
      return "shared";
    }
  } catch (e) {
    // User cancel — treat as soft fail without clipboard overwrite
    if (e instanceof DOMException && e.name === "AbortError") return "failed";
  }
  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(`${payload.title}\n\n${payload.text}`);
      return "copied";
    }
  } catch {
    /* ignore */
  }
  return "failed";
}

type TodayLike = {
  day_label?: string;
  focus?: string;
  program_name?: string;
  exercises?: {
    exercise: string;
    sets: number;
    logged_sets: { weight_lbs: number | null; reps: number | null; is_pr?: boolean }[];
  }[];
  debrief?: { headline?: string; message?: string; completion_pct?: number; prs?: string[] } | null;
};

export function formatSessionShare(plan: TodayLike): Shareable {
  const lines: string[] = [];
  lines.push(plan.day_label || "Coach K session");
  if (plan.program_name) lines.push(plan.program_name);
  if (plan.focus) lines.push(plan.focus);
  lines.push("");
  for (const ex of plan.exercises || []) {
    const logged = ex.logged_sets || [];
    if (!logged.length) continue;
    const sets = logged
      .map((s) => `${s.weight_lbs ?? "—"}×${s.reps ?? "—"}${s.is_pr ? " PR" : ""}`)
      .join(", ");
    lines.push(`${ex.exercise}: ${sets}`);
  }
  if (plan.debrief?.headline) {
    lines.push("", plan.debrief.headline);
  }
  if (plan.debrief?.message) {
    lines.push(plan.debrief.message.replace(/\*\*/g, ""));
  }
  if (plan.debrief?.prs?.length) {
    lines.push("", `PRs: ${plan.debrief.prs.join(", ")}`);
  }
  lines.push("", "— Coach K");
  return { title: "Coach K · Session", text: lines.join("\n").trim() };
}

type ProgressLike = {
  days: number;
  sessions: number;
  load_summary?: { acwr: number | null; sessions_28d?: number };
  lifts?: Record<
    string,
    { current: number; delta: number; delta_pct: number }
  >;
  prs?: { date: string; exercise: string; weight_lbs: number | null; reps: number | null }[];
  goal_mode?: string;
};

export function formatProgressShare(data: ProgressLike): Shareable {
  const lines: string[] = [`Coach K progress · last ${data.days} days`];
  if (data.goal_mode) lines.push(`Mode: ${data.goal_mode}`);
  lines.push(`Sessions: ${data.sessions}`);
  if (data.load_summary?.acwr != null) {
    lines.push(`ACWR: ${data.load_summary.acwr}`);
  }
  lines.push("");
  const lifts = data.lifts || {};
  for (const [k, L] of Object.entries(lifts)) {
    const sign = L.delta >= 0 ? "+" : "";
    lines.push(
      `${k}: ${Math.round(L.current)} lbs e1RM (${sign}${Math.round(L.delta)} / ${sign}${L.delta_pct}%)`,
    );
  }
  const recent = (data.prs || []).slice(0, 5);
  if (recent.length) {
    lines.push("", "Recent PRs:");
    for (const p of recent) {
      lines.push(
        `· ${p.date} ${p.exercise} ${p.weight_lbs ?? "—"}×${p.reps ?? "—"}`,
      );
    }
  }
  lines.push("", "— Coach K");
  return { title: "Coach K · Progress", text: lines.join("\n") };
}

export function formatWeeklyReviewShare(review: {
  title?: string;
  message?: string;
  wins?: string[];
  focuses?: string[];
  week_of?: string;
}): Shareable {
  const lines: string[] = [review.title || "Coach K weekly review"];
  if (review.week_of) lines.push(`Week of ${review.week_of}`);
  lines.push("");
  if (review.message) lines.push(review.message.replace(/\*\*/g, ""));
  if (review.wins?.length) {
    lines.push("", "Wins:");
    for (const w of review.wins) lines.push(`· ${w}`);
  }
  if (review.focuses?.length) {
    lines.push("", "Focus:");
    for (const f of review.focuses) lines.push(`· ${f}`);
  }
  lines.push("", "— Coach K");
  return { title: "Coach K · Weekly review", text: lines.join("\n").trim() };
}

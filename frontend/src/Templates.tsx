import { useEffect, useState } from "react";
import { api, Template, TemplateEx } from "./api";

const GOALS = ["all", "strength", "hypertrophy", "athleticism", "general"] as const;

export function FlipImage({ urls, size = 56 }: { urls: string[]; size?: number }) {
  const [f, setF] = useState(0);
  useEffect(() => {
    if (urls.length < 2) return;
    const t = setInterval(() => setF((x) => 1 - x), 900);
    return () => clearInterval(t);
  }, [urls]);
  if (!urls.length) return <div style={{ width: size, height: size }} className="shrink-0 rounded-lg bg-ink" />;
  return (
    <img
      src={urls[f] ?? urls[0]}
      style={{ width: size, height: size }}
      className="shrink-0 rounded-lg border border-line bg-white object-cover"
      alt=""
    />
  );
}

export default function Templates({
  onPersonalize,
  onActivated,
}: {
  onPersonalize: (name: string) => void;
  onActivated?: () => void;
}) {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [goal, setGoal] = useState<(typeof GOALS)[number]>("all");
  const [open, setOpen] = useState<Template | null>(null);
  const [activating, setActivating] = useState(false);
  const [activateMsg, setActivateMsg] = useState("");

  useEffect(() => {
    api("/api/templates")
      .then((r) => {
        if (r.ok) r.json().then(setTemplates);
      })
      .catch(() => {});
  }, []);

  const shown = templates.filter((t) => goal === "all" || t.goal === goal);

  async function startPlan(id: string) {
    setActivating(true);
    setActivateMsg("");
    const r = await api("/api/templates/activate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ template_id: id }),
    });
    setActivating(false);
    if (!r.ok) {
      const d = await r.json().catch(() => ({}));
      setActivateMsg(typeof d.detail === "string" ? d.detail : "Couldn't activate plan");
      return;
    }
    const data = await r.json();
    setActivateMsg(`Active: ${data.name}`);
    onActivated?.();
  }

  if (open) {
    return (
      <div className="mx-auto w-full max-w-3xl flex-1 overflow-y-auto px-4 py-5 sm:px-6 sm:py-6">
        <button onClick={() => setOpen(null)} className="mb-4 text-sm text-mut hover:text-white">
          ← All plans
        </button>
        <p className="ck-eyebrow">
          {(open.source_type || "book").toUpperCase()} · {open.days_per_week} DAYS/WK
        </p>
        <h2 className="mt-2 font-display text-xl font-black tracking-tight sm:text-2xl">{open.name}</h2>
        <p className="mt-2 text-sm leading-relaxed text-mut">{open.summary}</p>
        <p className="mt-2 text-xs leading-relaxed text-brand">{open.based_on}</p>
        <div className="mt-5 flex flex-wrap gap-2">
          <button
            onClick={() => startPlan(open.id)}
            disabled={activating}
            className="ck-btn ck-btn-primary"
          >
            {activating ? "Starting…" : "Start this plan"}
          </button>
          <button
            onClick={() => onPersonalize(open.name)}
            className="ck-btn ck-btn-ghost"
          >
            Personalize with Coach K
          </button>
        </div>
        {activateMsg && <p className="mt-3 text-sm text-emerald-400">{activateMsg}</p>}
        <div className="mt-6 space-y-6">
          {open.days.map((d) => (
            <section key={d.label} className="ck-surface p-4">
              <h3 className="mb-3 font-display font-bold">{d.label}</h3>
              <ul className="space-y-3">
                {d.exercises.map((ex: TemplateEx) => (
                  <li key={ex.name} className="flex items-center gap-3">
                    <FlipImage urls={ex.image_urls} />
                    <div>
                      <p className="text-sm font-semibold">{ex.name}</p>
                      <p className="text-xs text-mut">
                        {ex.sets} × {ex.reps} · {ex.intensity}
                      </p>
                    </div>
                  </li>
                ))}
              </ul>
            </section>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto w-full max-w-3xl flex-1 overflow-y-auto px-4 py-5 sm:px-6 sm:py-6">
      <div className="relative mb-6 overflow-hidden rounded-2xl border border-line">
        <img
          src="/images/rack-focus.jpg"
          alt=""
          className="absolute inset-0 h-full w-full object-cover opacity-35"
        />
        <div className="absolute inset-0 bg-gradient-to-r from-ink via-ink/85 to-ink/40" />
        <div className="relative px-5 py-8 sm:px-7 sm:py-10">
          <p className="ck-eyebrow">Library</p>
          <h2 className="mt-2 font-display text-2xl font-black tracking-tight sm:text-3xl">
            Pre-Made Plans
          </h2>
          <p className="mt-2 max-w-lg text-sm leading-relaxed text-fg-dim">
            Book-inspired starting points. Tap a plan, then <strong className="text-white">Start this plan</strong> to
            train today — or ask Coach K to personalize it.
          </p>
        </div>
      </div>
      <div className="flex flex-wrap gap-2">
        {GOALS.map((g) => (
          <button
            key={g}
            onClick={() => setGoal(g)}
            className={`rounded-lg px-3 py-1.5 text-xs font-semibold capitalize transition ${
              goal === g ? "bg-brand text-white" : "border border-line bg-panel text-mut hover:text-white"
            }`}
          >
            {g}
          </button>
        ))}
      </div>
      <p className="mt-3 text-xs text-mut">{shown.length} plans</p>
      <div className="mt-4 grid gap-4 sm:grid-cols-2">
        {shown.map((t) => (
          <button
            key={t.id}
            onClick={() => setOpen(t)}
            className="ck-surface p-4 text-left transition hover:border-brand"
          >
            <p className="font-display font-bold">{t.name}</p>
            <p className="mt-0.5 text-xs font-semibold uppercase tracking-wider text-brand">
              {t.goal} · {t.days_per_week} days/wk
              {t.source_type ? ` · ${t.source_type}` : ""}
            </p>
            <p className="mt-2 line-clamp-3 text-sm text-mut">{t.summary}</p>
            <p className="mt-2 text-[11px] leading-snug text-white/40">{t.based_on}</p>
          </button>
        ))}
      </div>
    </div>
  );
}

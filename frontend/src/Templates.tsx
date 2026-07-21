import { useEffect, useState } from "react";
import { api, Template, TemplateEx } from "./api";

const GOALS = ["all", "strength", "hypertrophy", "athleticism", "general"] as const;

// Start/end frames flipped on a timer — the "GIF" treatment.
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
    />
  );
}

export default function Templates({ onPersonalize }: { onPersonalize: (name: string) => void }) {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [goal, setGoal] = useState<(typeof GOALS)[number]>("all");
  const [open, setOpen] = useState<Template | null>(null);

  useEffect(() => {
    api("/api/templates")
      .then((r) => {
        if (r.ok) r.json().then(setTemplates);
      })
      .catch(() => {});
  }, []);

  const shown = templates.filter((t) => goal === "all" || t.goal === goal);

  if (open) {
    return (
      <div className="mx-auto w-full max-w-3xl flex-1 overflow-y-auto px-4 py-5 sm:px-6 sm:py-6">
        <button onClick={() => setOpen(null)} className="mb-4 text-sm text-mut hover:text-white">
          ← All templates
        </button>
        <h2 className="font-display text-xl font-black tracking-tight">{open.name}</h2>
        <p className="mt-1 text-sm text-mut">{open.summary}</p>
        <p className="mt-1 text-xs text-brand">{open.based_on}</p>
        <button
          onClick={() => onPersonalize(open.name)}
          className="mt-4 rounded-xl bg-brand px-4 py-2 text-sm font-semibold text-white"
        >
          Have Coach K personalize this →
        </button>
        <div className="mt-6 space-y-6">
          {open.days.map((d) => (
            <section key={d.label} className="rounded-xl bg-panel p-4">
              <h3 className="mb-3 font-bold">{d.label}</h3>
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
          <p className="font-display text-xs font-semibold tracking-[0.3em] text-brand">LIBRARY</p>
          <h2 className="mt-2 font-display text-2xl font-black tracking-tight sm:text-3xl">
            Plan Templates
          </h2>
          <p className="mt-2 max-w-lg text-sm leading-relaxed text-white/70">
            Book-grounded starting points. Pick one and Coach K adapts it to your profile, lifts, and readiness.
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
      <div className="mt-5 grid gap-4 sm:grid-cols-2">
        {shown.map((t) => (
          <button
            key={t.id}
            onClick={() => setOpen(t)}
            className="rounded-xl border border-line bg-panel/80 p-4 text-left transition hover:border-brand"
          >
            <p className="font-display font-bold">{t.name}</p>
            <p className="mt-0.5 text-xs font-semibold uppercase tracking-wider text-brand">
              {t.goal} · {t.days_per_week} days/wk
            </p>
            <p className="mt-2 text-sm text-mut">{t.summary}</p>
          </button>
        ))}
      </div>
    </div>
  );
}

/**
 * First-run onboarding — one job per step, brand-forward, no dashboard clutter.
 * Persists profile + optional starter plan, then marks onboarded.
 */

import { useMemo, useState } from "react";
import { api, Template } from "./api";

const GOAL_MODES = [
  { id: "athleticism", label: "Athleticism", blurb: "Jump, power, court transfer" },
  { id: "strength", label: "Strength", blurb: "Heavier compounds, clear PRs" },
  { id: "hypertrophy", label: "Size", blurb: "Volume and muscle priorities" },
  { id: "recomposition", label: "Recomp", blurb: "Strength + sharper physique" },
  { id: "general", label: "General", blurb: "Stay capable and consistent" },
] as const;

const SCHEDULES = [
  { id: "2 days/week", days: 2 },
  { id: "3 days/week", days: 3 },
  { id: "4 days/week", days: 4 },
  { id: "5–6 days/week", days: 6 },
] as const;

const EQUIPMENT = [
  "Full barbell gym",
  "Dumbbells + bench",
  "Hotel / minimal",
  "Mixed / whatever's open",
] as const;

type Props = {
  onComplete: () => void;
};

export default function Onboarding({ onComplete }: Props) {
  const [step, setStep] = useState(0);
  const [name, setName] = useState("");
  const [goalMode, setGoalMode] = useState<string>("athleticism");
  const [schedule, setSchedule] = useState("3 days/week");
  const [equipment, setEquipment] = useState<string>(EQUIPMENT[0]);
  const [bodyweight, setBodyweight] = useState("");
  const [squat, setSquat] = useState("");
  const [bench, setBench] = useState("");
  const [deadlift, setDeadlift] = useState("");
  const [templates, setTemplates] = useState<Template[]>([]);
  const [pickedPlan, setPickedPlan] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const daysWanted = useMemo(
    () => SCHEDULES.find((s) => s.id === schedule)?.days ?? 3,
    [schedule],
  );

  async function loadPlans() {
    const r = await api("/api/templates");
    if (!r.ok) return;
    const all: Template[] = await r.json();
    const filtered = all.filter(
      (t) =>
        (t.goal === goalMode || (goalMode === "recomposition" && t.goal === "hypertrophy")) &&
        Math.abs(t.days_per_week - daysWanted) <= 1,
    );
    setTemplates(filtered.length ? filtered : all.slice(0, 6));
  }

  async function goNext() {
    setError("");
    if (step === 0 && !name.trim()) {
      setError("What should Coach K call you?");
      return;
    }
    if (step === 4) {
      await loadPlans();
    }
    setStep((s) => Math.min(s + 1, 5));
  }

  async function finish(activatePlanId: string | null) {
    setBusy(true);
    setError("");
    try {
      const lifts: Record<string, number> = {};
      if (squat) lifts.squat = Number(squat);
      if (bench) lifts.bench = Number(bench);
      if (deadlift) lifts.deadlift = Number(deadlift);

      const r = await api("/api/onboarding", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: name.trim(),
          goal_mode: goalMode,
          schedule,
          equipment,
          bodyweight_lbs: bodyweight ? Number(bodyweight) : null,
          lifts_1rm: Object.keys(lifts).length ? lifts : null,
          template_id: activatePlanId,
        }),
      });
      if (!r.ok) {
        const d = await r.json().catch(() => ({}));
        throw new Error(d.detail || "Couldn't save onboarding");
      }
      localStorage.setItem("coachk_onboarded", "1");
      onComplete();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong");
    } finally {
      setBusy(false);
    }
  }

  const steps = ["You", "Goal", "Schedule", "Gear", "Numbers", "Plan"];
  const progress = ((step + 1) / steps.length) * 100;

  return (
    <div className="fixed inset-0 z-50 flex flex-col bg-paper">
      <div className="pointer-events-none absolute inset-0 opacity-20">
        <img src="/images/hero-barbell.jpg" alt="" className="h-full w-full object-cover" />
        <div className="absolute inset-0 bg-gradient-to-t from-paper via-paper/90 to-paper/70" />
      </div>

      <header className="relative z-10 px-5 pt-[calc(1rem+env(safe-area-inset-top))] sm:px-8">
        <div className="mx-auto flex max-w-lg items-center justify-between">
          <span className="ck-mark text-sm">COACH K</span>
          <span className="text-xs text-mut">
            {step + 1} / {steps.length}
          </span>
        </div>
        <div className="mx-auto mt-4 h-1 max-w-lg overflow-hidden bg-line">
          <div
            className="h-full bg-brand transition-all duration-500"
            style={{ width: `${progress}%` }}
          />
        </div>
      </header>

      <main className="relative z-10 mx-auto flex w-full max-w-lg flex-1 flex-col px-5 py-8 sm:px-8">
        {step === 0 && (
          <section className="animate-rise flex flex-1 flex-col">
            <p className="ck-eyebrow">Welcome</p>
            <h1 className="mt-3 font-display text-4xl font-black tracking-tight sm:text-5xl">
              Let's build your training base.
            </h1>
            <p className="mt-3 text-base leading-relaxed text-fg-dim">
              A few details so Coach K programs for <em>you</em> — not a generic PDF.
            </p>
            <label className="mt-10 block">
              <span className="mb-2 block text-xs font-semibold uppercase tracking-wider text-mut">
                Your name
              </span>
              <input
                className="ck-field"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Dayan"
                autoFocus
              />
            </label>
          </section>
        )}

        {step === 1 && (
          <section className="animate-rise flex flex-1 flex-col">
            <p className="ck-eyebrow">Goal mode</p>
            <h1 className="mt-3 font-display text-3xl font-black tracking-tight sm:text-4xl">
              What are we training for?
            </h1>
            <div className="mt-8 grid gap-2">
              {GOAL_MODES.map((g) => (
                <button
                  key={g.id}
                  type="button"
                  onClick={() => setGoalMode(g.id)}
                  className={`border px-4 py-3.5 text-left transition ${
                    goalMode === g.id
                      ? "border-brand bg-brand/5"
                      : "border-line bg-panel hover:border-brand"
                  }`}
                >
                  <span className="font-display font-bold">{g.label}</span>
                  <span className="mt-0.5 block text-sm text-mut">{g.blurb}</span>
                </button>
              ))}
            </div>
          </section>
        )}

        {step === 2 && (
          <section className="animate-rise flex flex-1 flex-col">
            <p className="ck-eyebrow">Schedule</p>
            <h1 className="mt-3 font-display text-3xl font-black tracking-tight">
              How often can you train?
            </h1>
            <div className="mt-8 grid grid-cols-2 gap-2">
              {SCHEDULES.map((s) => (
                <button
                  key={s.id}
                  type="button"
                  onClick={() => setSchedule(s.id)}
                  className={`border px-4 py-4 text-left font-semibold transition ${
                    schedule === s.id
                      ? "border-brand bg-brand/5"
                      : "border-line bg-panel hover:border-brand"
                  }`}
                >
                  {s.id}
                </button>
              ))}
            </div>
          </section>
        )}

        {step === 3 && (
          <section className="animate-rise flex flex-1 flex-col">
            <p className="ck-eyebrow">Equipment</p>
            <h1 className="mt-3 font-display text-3xl font-black tracking-tight">
              What do you train with?
            </h1>
            <div className="mt-8 grid gap-2">
              {EQUIPMENT.map((e) => (
                <button
                  key={e}
                  type="button"
                  onClick={() => setEquipment(e)}
                  className={`border px-4 py-3.5 text-left font-semibold transition ${
                    equipment === e
                      ? "border-brand bg-brand/5"
                      : "border-line bg-panel hover:border-brand"
                  }`}
                >
                  {e}
                </button>
              ))}
            </div>
          </section>
        )}

        {step === 4 && (
          <section className="animate-rise flex flex-1 flex-col">
            <p className="ck-eyebrow">Numbers</p>
            <h1 className="mt-3 font-display text-3xl font-black tracking-tight">
              Optional — but powerful.
            </h1>
            <p className="mt-2 text-sm text-mut">
              Bodyweight and 1RMs let Coach K prescribe real loads. Skip any you don't know.
            </p>
            <div className="mt-8 space-y-3">
              <label className="block">
                <span className="mb-1 block text-xs font-semibold uppercase tracking-wider text-mut">
                  Bodyweight (lbs)
                </span>
                <input className="ck-field" inputMode="decimal" value={bodyweight} onChange={(e) => setBodyweight(e.target.value)} placeholder="e.g. 210" />
              </label>
              <div className="grid grid-cols-3 gap-2">
                {[
                  ["Squat", squat, setSquat],
                  ["Bench", bench, setBench],
                  ["Deadlift", deadlift, setDeadlift],
                ].map(([label, val, set]) => (
                  <label key={label as string} className="block">
                    <span className="mb-1 block text-[10px] font-semibold uppercase tracking-wider text-mut">
                      {label as string} 1RM
                    </span>
                    <input
                      className="ck-field px-2 text-center"
                      inputMode="decimal"
                      value={val as string}
                      onChange={(e) => (set as (v: string) => void)(e.target.value)}
                      placeholder="—"
                    />
                  </label>
                ))}
              </div>
            </div>
          </section>
        )}

        {step === 5 && (
          <section className="animate-rise flex flex-1 flex-col">
            <p className="ck-eyebrow">Starter plan</p>
            <h1 className="mt-3 font-display text-3xl font-black tracking-tight">
              Pick a starting block.
            </h1>
            <p className="mt-2 text-sm text-mut">
              Book-inspired plans matched to your goal and schedule. You can change anytime.
            </p>
            <div className="mt-6 max-h-[45vh] space-y-2 overflow-y-auto pr-1">
              {templates.map((t) => (
                <button
                  key={t.id}
                  type="button"
                  onClick={() => setPickedPlan(t.id)}
                  className={`w-full border px-4 py-3 text-left transition ${
                    pickedPlan === t.id
                      ? "border-brand bg-brand/5"
                      : "border-line bg-panel hover:border-brand"
                  }`}
                >
                  <span className="font-display font-bold">{t.name}</span>
                  <span className="mt-0.5 block text-xs text-brand">
                    {t.goal} · {t.days_per_week} days/wk
                  </span>
                  <span className="mt-1 line-clamp-2 block text-xs text-mut">{t.summary}</span>
                </button>
              ))}
            </div>
          </section>
        )}

        {error && <p className="mt-4 text-sm text-brand">{error}</p>}

        <footer className="mt-auto flex gap-2 pb-[calc(1rem+env(safe-area-inset-bottom))] pt-8">
          {step > 0 && (
            <button type="button" className="ck-btn ck-btn-ghost flex-1" onClick={() => setStep((s) => s - 1)} disabled={busy}>
              Back
            </button>
          )}
          {step < 5 ? (
            <button type="button" className="ck-btn ck-btn-primary flex-[2]" onClick={goNext}>
              Continue
            </button>
          ) : (
            <>
              <button
                type="button"
                className="ck-btn ck-btn-ghost flex-1"
                disabled={busy}
                onClick={() => finish(null)}
              >
                Skip plan
              </button>
              <button
                type="button"
                className="ck-btn ck-btn-primary flex-[2]"
                disabled={busy || !pickedPlan}
                onClick={() => finish(pickedPlan)}
              >
                {busy ? "Saving…" : "Start training"}
              </button>
            </>
          )}
        </footer>
      </main>
    </div>
  );
}

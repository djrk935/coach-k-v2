import { useEffect, useRef, useState } from "react";
import { api, LoggedSet, TodayExercise, TodayPlan } from "./api";
import { FlipImage } from "./Templates";

function parseRepTarget(reps: string): number | undefined {
  const m = reps.match(/\d+/);
  return m ? Number(m[0]) : undefined;
}

type SpeechRecognitionLike = {
  lang: string;
  onresult: ((e: { results: { transcript: string }[][] }) => void) | null;
  onerror: (() => void) | null;
  onend: (() => void) | null;
  start: () => void;
  stop: () => void;
};

function getSpeechRecognition(): (new () => SpeechRecognitionLike) | null {
  const w = window as unknown as Record<string, unknown>;
  return (w.SpeechRecognition ?? w.webkitSpeechRecognition ?? null) as
    | (new () => SpeechRecognitionLike)
    | null;
}

function ExerciseCard({
  ex,
  slot,
  onLog,
  onSwap,
}: {
  ex: TodayExercise;
  slot: number;
  onLog: (
    slot: number, exercise: string, weight: number | null, reps: number | null, rir: number | null,
  ) => Promise<void>;
  onSwap?: (slot: number, newExercise: string) => Promise<void>;
}) {
  const [weight, setWeight] = useState(
    ex.suggested_weight_lbs != null ? String(ex.suggested_weight_lbs) : "",
  );
  const [reps, setReps] = useState(String(parseRepTarget(ex.reps) ?? ""));
  const [busy, setBusy] = useState(false);
  const done = ex.logged_sets.length;
  const target = ex.sets;
  const lastPr = ex.logged_sets.some((s) => s.is_pr);

  useEffect(() => {
    setWeight(ex.suggested_weight_lbs != null ? String(ex.suggested_weight_lbs) : "");
  }, [ex.suggested_weight_lbs, ex.exercise]);

  async function logSet() {
    setBusy(true);
    await onLog(slot, ex.exercise, weight ? Number(weight) : null, reps ? Number(reps) : null, null);
    setBusy(false);
  }

  return (
    <div className="rounded-xl border border-line bg-panel p-3 sm:p-4">
      <div className="flex items-start gap-3">
        <FlipImage urls={ex.image_urls} size={44} />
        <div className="min-w-0 flex-1">
          <div className="flex min-w-0 items-center gap-2">
            {ex.superset_group && (
              <span className="shrink-0 rounded bg-brand px-1.5 py-0.5 text-[10px] font-extrabold text-white">
                {ex.superset_group}
              </span>
            )}
            <p className="truncate font-bold">{ex.exercise}</p>
            {ex.swapped && <span className="shrink-0 text-[10px] text-brand">swap</span>}
            {ex.adapted && <span className="shrink-0 text-[10px] text-amber-400">adapted</span>}
            {lastPr && <span className="shrink-0 text-xs text-brand">PR</span>}
          </div>
          <p className="text-xs text-mut">
            {target} × {ex.reps} · {ex.intensity}
            {ex.notes ? ` · ${ex.notes}` : ""}
          </p>
          {ex.form_cue && (
            <p className="mt-1 text-[11px] leading-snug text-white/55">{ex.form_cue}</p>
          )}
          {ex.progression && (
            <p className="mt-1 text-[11px] text-emerald-400">{ex.progression.reason}</p>
          )}
          {ex.swap_suggestion && onSwap && (
            <button
              onClick={() => onSwap(slot, ex.swap_suggestion!)}
              className="mt-1.5 text-[11px] font-semibold text-brand hover:underline"
            >
              Swap → {ex.swap_suggestion}
            </button>
          )}
        </div>
        <div className="shrink-0 text-right text-xs font-semibold text-mut">
          {done}/{target} sets
        </div>
      </div>

      {ex.logged_sets.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-1.5">
          {ex.logged_sets.map((s: LoggedSet, i) => (
            <span
              key={i}
              className={`rounded-lg px-2 py-0.5 text-xs ${
                s.is_pr ? "bg-brand text-white" : "bg-ink text-mut"
              }`}
            >
              {s.weight_lbs ?? "—"}×{s.reps ?? "—"}
            </span>
          ))}
        </div>
      )}

      <div className="mt-3 flex min-w-0 items-center gap-2">
        <input
          value={weight}
          onChange={(e) => setWeight(e.target.value)}
          inputMode="decimal"
          placeholder="lbs"
          className="w-16 shrink-0 rounded-lg border border-line bg-ink px-1.5 py-2.5 text-center text-sm outline-none focus:border-brand sm:w-20 sm:px-2"
        />
        <span className="shrink-0 text-mut">×</span>
        <input
          value={reps}
          onChange={(e) => setReps(e.target.value)}
          inputMode="numeric"
          placeholder="reps"
          className="w-14 shrink-0 rounded-lg border border-line bg-ink px-1.5 py-2.5 text-center text-sm outline-none focus:border-brand sm:w-16 sm:px-2"
        />
        <button
          onClick={logSet}
          disabled={busy || done >= target}
          className="min-w-0 flex-1 rounded-lg bg-brand py-2.5 text-sm font-bold text-white disabled:opacity-40"
        >
          {done >= target ? "✓ Done" : "Log Set"}
        </button>
      </div>
    </div>
  );
}

function CheckinGate({
  onDone,
}: {
  onDone: () => void;
}) {
  const [sleep, setSleep] = useState("7");
  const [soreness, setSoreness] = useState("3");
  const [stress, setStress] = useState("3");
  const [busy, setBusy] = useState(false);

  async function submit() {
    setBusy(true);
    await api("/api/today/checkin", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        sleep_h: Number(sleep),
        soreness_0_10: Number(soreness),
        stress_0_10: Number(stress),
      }),
    });
    setBusy(false);
    onDone();
  }

  return (
    <div className="mb-5 rounded-2xl border border-brand/40 bg-panel p-4">
      <p className="font-display text-xs font-semibold tracking-[0.25em] text-brand">CHECK-IN</p>
      <p className="mt-1 text-sm text-mut">Quick readiness before you train — Coach K adapts the day.</p>
      <div className="mt-4 grid grid-cols-3 gap-2">
        {[
          { label: "Sleep (h)", value: sleep, set: setSleep },
          { label: "Soreness", value: soreness, set: setSoreness },
          { label: "Stress", value: stress, set: setStress },
        ].map((f) => (
          <label key={f.label} className="block">
            <span className="mb-1 block text-[10px] font-semibold uppercase tracking-wider text-mut">
              {f.label}
            </span>
            <input
              value={f.value}
              onChange={(e) => f.set(e.target.value)}
              inputMode="decimal"
              className="w-full rounded-lg border border-line bg-ink px-2 py-2 text-center text-sm outline-none focus:border-brand"
            />
          </label>
        ))}
      </div>
      <button
        onClick={submit}
        disabled={busy}
        className="mt-4 w-full rounded-xl bg-brand py-2.5 text-sm font-bold text-white disabled:opacity-40"
      >
        {busy ? "Saving…" : "Set today's plan"}
      </button>
    </div>
  );
}

export default function Today({ onGoToTemplates }: { onGoToTemplates: () => void }) {
  const [plan, setPlan] = useState<TodayPlan | null>(null);
  const [loading, setLoading] = useState(true);
  const [finished, setFinished] = useState(false);
  const [debrief, setDebrief] = useState<TodayPlan["debrief"] | null>(null);
  const [listening, setListening] = useState(false);
  const [heard, setHeard] = useState("");
  const recogRef = useRef<SpeechRecognitionLike | null>(null);

  const load = () =>
    api("/api/today")
      .then((r) => (r.ok ? r.json() : { active: false }))
      .then((d) => {
        setPlan(d);
        setLoading(false);
      })
      .catch(() => setLoading(false));

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function logSet(
    slot: number, exercise: string, weight: number | null, reps: number | null, rir: number | null,
  ) {
    if (!plan) return;
    const r = await api("/api/today/log-set", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        program_id: plan.program_id, day_index: plan.day_index, slot_index: slot,
        exercise, weight_lbs: weight, reps, rir,
      }),
    });
    if (r.ok) await load();
  }

  async function swap(slot: number, newExercise: string) {
    if (!plan) return;
    await api("/api/today/swap", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        program_id: plan.program_id,
        day_index: plan.day_index,
        slot_index: slot,
        new_exercise: newExercise,
      }),
    });
    await load();
  }

  async function catchUp(action: string) {
    if (!plan) return;
    await api("/api/today/catch-up", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ program_id: plan.program_id, action }),
    });
    await load();
  }

  async function finishWorkout() {
    if (!plan) return;
    const r = await api("/api/today/finish", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ program_id: plan.program_id, day_index: plan.day_index }),
    });
    const data = r.ok ? await r.json() : {};
    setDebrief(data.debrief ?? null);
    setFinished(true);
  }

  function startVoice() {
    const SR = getSpeechRecognition();
    if (!SR || !plan) return;
    const rec = new SR();
    rec.lang = "en-US";
    rec.onresult = async (e) => {
      const transcript = e.results[0]?.[0]?.transcript ?? "";
      setHeard(transcript);
      const r = await api("/api/today/log-voice", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: transcript,
          program_id: plan.program_id,
          day_index: plan.day_index,
          exercise_names: plan.exercises.map((ex) => ex.exercise),
        }),
      });
      const data = await r.json().catch(() => ({ matched: false }));
      if (data.matched) await load();
      else if (data.detail) setHeard(`⚠ ${data.detail}`);
      else setHeard(`Couldn't match that to today's exercises: "${transcript}"`);
    };
    rec.onerror = () => setListening(false);
    rec.onend = () => setListening(false);
    recogRef.current = rec;
    rec.start();
    setListening(true);
  }

  if (loading) return <div className="flex-1" />;

  if (!plan?.active) {
    return (
      <div className="relative flex flex-1 flex-col items-center justify-center overflow-hidden px-6 text-center">
        <img
          src="/images/training-floor.jpg"
          alt=""
          className="absolute inset-0 h-full w-full object-cover opacity-30"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-ink via-ink/85 to-ink/50" />
        <div className="relative animate-rise">
          <p className="font-display text-xs font-semibold tracking-[0.3em] text-brand">TODAY</p>
          <p className="mt-3 font-display text-2xl font-black tracking-tight">No active program yet.</p>
          <p className="mt-2 max-w-sm text-sm text-mut">
            Pick a book-inspired plan or ask Coach K to build one around your goals.
          </p>
          <button
            onClick={onGoToTemplates}
            className="mt-6 rounded-xl bg-brand px-5 py-2.5 text-sm font-bold text-white transition hover:brightness-110"
          >
            Browse Plans →
          </button>
        </div>
      </div>
    );
  }

  if (finished) {
    return (
      <div className="relative flex flex-1 flex-col items-center justify-center overflow-hidden px-6 text-center">
        <img
          src="/images/chalk-hands.jpg"
          alt=""
          className="absolute inset-0 h-full w-full object-cover opacity-25"
        />
        <div className="absolute inset-0 bg-ink/80" />
        <div className="relative animate-rise max-w-md">
          <p className="font-display text-xs font-semibold tracking-[0.3em] text-brand">SESSION</p>
          <p className="mt-3 font-display text-2xl font-black tracking-tight">
            {debrief?.headline ?? "Day complete — nice work."}
          </p>
          {debrief?.message && (
            <p className="mt-4 whitespace-pre-line text-left text-sm leading-relaxed text-white/75">
              {debrief.message.replace(/\*\*/g, "")}
            </p>
          )}
          <button
            onClick={() => {
              setFinished(false);
              setDebrief(null);
              setLoading(true);
              load();
            }}
            className="mt-6 rounded-xl border border-line px-5 py-2.5 text-sm font-semibold hover:border-brand"
          >
            See what's next →
          </button>
        </div>
      </div>
    );
  }

  const allDone = plan.exercises.every((ex) => ex.logged_sets.length >= ex.sets);
  const adapt = plan.adaptation;
  const needsCheckin = adapt?.needs_checkin;

  return (
    <div className="mx-auto w-full max-w-2xl flex-1 overflow-y-auto px-4 py-5 pb-[calc(1.25rem+env(safe-area-inset-bottom))] sm:px-6 sm:py-6">
      {needsCheckin && <CheckinGate onDone={load} />}

      {plan.catch_up && (
        <div className="mb-4 rounded-xl border border-line bg-panel p-4">
          <p className="text-sm font-semibold">{plan.catch_up.message}</p>
          <div className="mt-3 flex flex-wrap gap-2">
            {[
              { id: "resume", label: "Resume plan" },
              { id: "repeat_last", label: "Repeat this day" },
              { id: "light_makeup", label: "Light makeup" },
            ].map((o) => (
              <button
                key={o.id}
                onClick={() => catchUp(o.id)}
                className="rounded-lg border border-line px-3 py-1.5 text-xs font-semibold hover:border-brand"
              >
                {o.label}
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="mb-4 flex items-center justify-between gap-3">
        <div className="min-w-0">
          <h2 className="font-display text-xl font-black tracking-tight">{plan.day_label}</h2>
          <p className="text-sm text-mut">{plan.focus}</p>
          {plan.goal_mode && (
            <p className="mt-0.5 text-[11px] font-semibold uppercase tracking-wider text-brand">
              {plan.goal_mode} mode
            </p>
          )}
        </div>
        {getSpeechRecognition() && (
          <button
            onClick={startVoice}
            className={`h-11 w-11 shrink-0 rounded-full text-lg ${
              listening ? "animate-pulse bg-brand text-white" : "border border-line hover:border-brand"
            }`}
            title="Log a set by voice"
          >
            🎤
          </button>
        )}
      </div>

      {adapt && !needsCheckin && (
        <div className={`mb-4 rounded-xl border p-3 text-sm ${
          adapt.soft_day ? "border-amber-500/40 bg-amber-500/10" : "border-line bg-panel"
        }`}>
          <p className="font-semibold capitalize">
            Readiness: {adapt.status}
            {adapt.score != null ? ` · ${adapt.score}` : ""}
            {adapt.soft_day ? " · soft day" : ""}
          </p>
          <p className="mt-1 text-xs text-mut">{adapt.intensity_note}</p>
          {adapt.reasons?.[0] && (
            <p className="mt-1 text-xs text-white/60">{adapt.reasons[0]}</p>
          )}
        </div>
      )}

      {plan.nutrition_targets && typeof plan.nutrition_targets === "object" && (
        <p className="mb-3 text-[11px] text-mut">
          Nutrition anchor:{" "}
          {(plan.nutrition_targets as { protein_g?: number }).protein_g
            ? `${(plan.nutrition_targets as { protein_g?: number }).protein_g}g protein`
            : "see program"}
          {(plan.nutrition_targets as { calories?: number }).calories
            ? ` · ${(plan.nutrition_targets as { calories?: number }).calories} kcal`
            : ""}
        </p>
      )}

      {heard && <p className="mb-3 text-xs text-mut">Heard: "{heard}"</p>}

      <div className="space-y-3">
        {plan.exercises.map((ex, i) => (
          <ExerciseCard key={`${ex.exercise}-${i}`} ex={ex} slot={i} onLog={logSet} onSwap={swap} />
        ))}
      </div>

      <button
        onClick={finishWorkout}
        className="mt-5 w-full rounded-xl bg-brand py-3 font-bold text-white"
      >
        {allDone ? "Finish Workout ✓" : "Finish Workout Anyway"}
      </button>
    </div>
  );
}

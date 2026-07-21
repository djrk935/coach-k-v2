import { useEffect, useRef, useState } from "react";
import { api, LoggedSet, TodayExercise, TodayPlan } from "./api";
import { FlipImage } from "./Templates";

function parseRepTarget(reps: string): number | undefined {
  const m = reps.match(/\d+/);
  return m ? Number(m[0]) : undefined;
}

// Web Speech API isn't in lib.dom.d.ts — minimal ambient shape for what we use.
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
}: {
  ex: TodayExercise;
  slot: number;
  onLog: (
    slot: number, exercise: string, weight: number | null, reps: number | null, rir: number | null,
  ) => Promise<void>;
}) {
  const [weight, setWeight] = useState(
    ex.suggested_weight_lbs != null ? String(ex.suggested_weight_lbs) : "",
  );
  const [reps, setReps] = useState(String(parseRepTarget(ex.reps) ?? ""));
  const [busy, setBusy] = useState(false);
  const done = ex.logged_sets.length;
  const target = ex.sets;
  const lastPr = ex.logged_sets.some((s) => s.is_pr);

  async function logSet() {
    setBusy(true);
    await onLog(slot, ex.exercise, weight ? Number(weight) : null, reps ? Number(reps) : null, null);
    setBusy(false);
  }

  return (
    <div className="rounded-xl border border-line bg-panel p-4">
      <div className="flex items-start gap-3">
        <FlipImage urls={ex.image_urls} size={44} />
        <div className="flex-1">
          <div className="flex items-center gap-2">
            {ex.superset_group && (
              <span className="rounded bg-brand px-1.5 py-0.5 text-[10px] font-extrabold text-white">
                {ex.superset_group}
              </span>
            )}
            <p className="font-bold">{ex.exercise}</p>
            {lastPr && <span className="text-xs">🎉 PR</span>}
          </div>
          <p className="text-xs text-mut">
            {target} × {ex.reps} · {ex.intensity}
            {ex.notes ? ` · ${ex.notes}` : ""}
          </p>
        </div>
        <div className="text-right text-xs font-semibold text-mut">
          {done}/{target} sets
        </div>
      </div>

      {ex.logged_sets.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-1.5">
          {ex.logged_sets.map((s: LoggedSet, i) => (
            <span
              key={i}
              className={`rounded-full px-2 py-0.5 text-xs ${
                s.is_pr ? "bg-brand text-white" : "bg-ink text-mut"
              }`}
            >
              {s.weight_lbs ?? "—"}×{s.reps ?? "—"}
            </span>
          ))}
        </div>
      )}

      <div className="mt-3 flex items-center gap-2">
        <input
          value={weight}
          onChange={(e) => setWeight(e.target.value)}
          inputMode="decimal"
          placeholder="lbs"
          className="w-20 rounded-lg border border-line bg-ink px-2 py-2.5 text-center text-sm outline-none focus:border-brand"
        />
        <span className="text-mut">×</span>
        <input
          value={reps}
          onChange={(e) => setReps(e.target.value)}
          inputMode="numeric"
          placeholder="reps"
          className="w-16 rounded-lg border border-line bg-ink px-2 py-2.5 text-center text-sm outline-none focus:border-brand"
        />
        <button
          onClick={logSet}
          disabled={busy || done >= target}
          className="flex-1 rounded-lg bg-brand py-2.5 text-sm font-bold text-white disabled:opacity-40"
        >
          {done >= target ? "✓ Done" : "Log Set"}
        </button>
      </div>
    </div>
  );
}

export default function Today({ onGoToTemplates }: { onGoToTemplates: () => void }) {
  const [plan, setPlan] = useState<TodayPlan | null>(null);
  const [loading, setLoading] = useState(true);
  const [finished, setFinished] = useState(false);
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

  async function finishWorkout() {
    if (!plan) return;
    await api("/api/today/finish", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ program_id: plan.program_id, day_index: plan.day_index }),
    });
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
      <div className="flex flex-1 flex-col items-center justify-center px-6 text-center">
        <p className="text-lg text-mut">No active program yet.</p>
        <p className="mt-1 text-sm text-mut">Pick a template or ask Coach K to build one.</p>
        <button onClick={onGoToTemplates} className="mt-4 rounded-xl bg-brand px-4 py-2 text-sm font-semibold text-white">
          Browse Templates →
        </button>
      </div>
    );
  }

  if (finished) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center px-6 text-center">
        <p className="text-3xl">✅</p>
        <p className="mt-2 text-lg font-bold">Day complete — nice work.</p>
        <button
          onClick={() => {
            setFinished(false);
            setLoading(true);
            load();
          }}
          className="mt-4 rounded-xl border border-line px-4 py-2 text-sm font-semibold hover:border-brand"
        >
          See what's next →
        </button>
      </div>
    );
  }

  const allDone = plan.exercises.every((ex) => ex.logged_sets.length >= ex.sets);

  return (
    <div className="flex-1 overflow-y-auto px-4 py-5 sm:px-6 sm:py-6">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h2 className="text-xl font-black">{plan.day_label}</h2>
          <p className="text-sm text-mut">{plan.focus}</p>
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
      {heard && <p className="mb-3 text-xs text-mut">🎤 "{heard}"</p>}

      <div className="space-y-3">
        {plan.exercises.map((ex, i) => (
          <ExerciseCard key={i} ex={ex} slot={i} onLog={logSet} />
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

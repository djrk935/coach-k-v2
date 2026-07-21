import { useEffect, useRef, useState } from "react";
import {
  api,
  FormCheckAssessment,
  InjuryProtocol,
  LoggedSet,
  TodayExercise,
  TodayPlan,
  videoToFrameDataUrls,
} from "./api";
import RestTimer from "./RestTimer";
import { formatSessionShare, shareContent } from "./share";
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
  const [showWarmup, setShowWarmup] = useState(true);
  const [warmupDone, setWarmupDone] = useState<Record<number, boolean>>({});
  const [formBusy, setFormBusy] = useState(false);
  const [formErr, setFormErr] = useState("");
  const [formResult, setFormResult] = useState<FormCheckAssessment | null>(null);
  const videoRef = useRef<HTMLInputElement>(null);
  const done = ex.logged_sets.length;
  const target = ex.sets;
  const lastPr = ex.logged_sets.some((s) => s.is_pr);
  const warmups = ex.warmup_sets ?? [];

  useEffect(() => {
    setWeight(ex.suggested_weight_lbs != null ? String(ex.suggested_weight_lbs) : "");
    setWarmupDone({});
    setFormResult(null);
    setFormErr("");
  }, [ex.suggested_weight_lbs, ex.exercise]);

  async function logSet() {
    setBusy(true);
    await onLog(slot, ex.exercise, weight ? Number(weight) : null, reps ? Number(reps) : null, null);
    setBusy(false);
  }

  function loadWarmup(i: number) {
    const w = warmups[i];
    if (!w) return;
    if (w.weight_lbs != null) setWeight(String(w.weight_lbs));
    setReps(String(w.reps));
    setWarmupDone((d) => ({ ...d, [i]: true }));
  }

  function loadWorking() {
    if (ex.suggested_weight_lbs != null) setWeight(String(ex.suggested_weight_lbs));
    setReps(String(parseRepTarget(ex.reps) ?? ""));
  }

  async function onVideoPicked(file: File | null) {
    if (!file) return;
    setFormBusy(true);
    setFormErr("");
    setFormResult(null);
    try {
      if (file.size > 80 * 1024 * 1024) {
        throw new Error("Keep the clip under ~80MB — a side-view set is enough.");
      }
      const frames = await videoToFrameDataUrls(file, { maxFrames: 5, maxDim: 960, maxSeconds: 20 });
      if (!frames.length) throw new Error("Couldn't pull frames from that clip.");
      const r = await api("/api/form-check", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          exercise: ex.exercise,
          images: frames,
          form_cue: ex.form_cue || undefined,
        }),
      });
      const data = await r.json().catch(() => ({}));
      if (!r.ok) throw new Error(data.detail || "Form check failed");
      setFormResult(data.assessment as FormCheckAssessment);
    } catch (e) {
      setFormErr(e instanceof Error ? e.message : "Form check failed");
    } finally {
      setFormBusy(false);
      if (videoRef.current) videoRef.current.value = "";
    }
  }

  const loadLabel =
    ex.suggested_weight_lbs != null ? `${ex.suggested_weight_lbs}` : "—";

  return (
    <div className="ck-row flex-col gap-3 sm:flex-row sm:items-start" style={{ animationDelay: `${slot * 30}ms` }}>
      <div className="flex w-full min-w-0 items-start gap-3">
        <span className="w-7 shrink-0 font-display text-xs font-bold tabular-nums text-mut">
          {String(slot + 1).padStart(2, "0")}
        </span>
        <FlipImage urls={ex.image_urls} size={40} />
        <div className="min-w-0 flex-1">
          <div className="flex min-w-0 items-center gap-2">
            {ex.superset_group && (
              <span className="shrink-0 bg-brand px-1.5 py-0.5 text-[10px] font-extrabold text-white">
                {ex.superset_group}
              </span>
            )}
            <p className="truncate font-display text-sm font-bold uppercase tracking-wide">{ex.exercise}</p>
            {ex.swapped && <span className="shrink-0 text-[10px] text-brand">swap</span>}
            {ex.adapted && <span className="shrink-0 text-[10px] text-amber-700">adapted</span>}
            {lastPr && <span className="shrink-0 text-xs font-bold text-brand">PR</span>}
          </div>
          <p className="text-xs text-mut">
            {target} × {ex.reps} · {ex.intensity}
            {ex.notes ? ` · ${ex.notes}` : ""}
          </p>
          {ex.form_cue && (
            <div className="ck-cue mt-2">
              <p className="ck-cue-label">Coach cue</p>
              <p className="mt-0.5 text-[12px] leading-snug">{ex.form_cue}</p>
            </div>
          )}
          {ex.progression && (
            <p className="mt-1 text-[11px] text-emerald-700">{ex.progression.reason}</p>
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
        <div className="shrink-0 text-right">
          <p className="font-display text-xl font-black tabular-nums leading-none text-brand sm:text-2xl">
            {loadLabel}
          </p>
          <p className="mt-1 text-[10px] font-semibold uppercase tracking-wider text-mut">
            {done}/{target} sets
          </p>
        </div>
      </div>

      {warmups.length > 0 && (
        <div className="mt-3 border border-line bg-paper p-2.5">
          <button
            type="button"
            onClick={() => setShowWarmup((s) => !s)}
            className="flex w-full items-center justify-between text-left"
          >
            <span className="text-[11px] font-semibold uppercase tracking-[0.18em] text-mut">
              Warm-up ramp
            </span>
            <span className="text-[11px] text-mut">{showWarmup ? "Hide" : "Show"}</span>
          </button>
          {showWarmup && (
            <div className="mt-2 space-y-1.5">
              {warmups.map((w, i) => (
                <button
                  key={`${w.label}-${i}`}
                  type="button"
                  onClick={() => loadWarmup(i)}
                  className={`flex w-full items-center justify-between border px-2.5 py-2 text-left text-xs transition ${
                    warmupDone[i]
                      ? "border-emerald-600/40 bg-emerald-50 text-emerald-700"
                      : "border-line bg-panel hover:border-brand"
                  }`}
                >
                  <span className="font-medium tabular-nums">{w.label}</span>
                  <span className="text-[10px] font-semibold uppercase tracking-wider text-mut">
                    {warmupDone[i] ? "Loaded" : "Load"}
                  </span>
                </button>
              ))}
              <button
                type="button"
                onClick={loadWorking}
                className="flex w-full items-center justify-between border border-brand bg-brand/5 px-2.5 py-2 text-left text-xs font-semibold text-brand"
              >
                <span>
                  Working set
                  {ex.suggested_weight_lbs != null ? ` · ${ex.suggested_weight_lbs} lbs` : ""}
                </span>
                <span className="text-[10px] uppercase tracking-wider">Load</span>
              </button>
            </div>
          )}
        </div>
      )}

      {ex.logged_sets.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-1.5">
          {ex.logged_sets.map((s: LoggedSet, i) => (
            <span
              key={i}
              className={`px-2 py-0.5 text-xs ${
                s.is_pr ? "bg-brand text-white" : "border border-line text-mut"
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
          className="ck-field w-16 shrink-0 py-2.5 text-center text-sm sm:w-20"
        />
        <span className="shrink-0 text-mut">×</span>
        <input
          value={reps}
          onChange={(e) => setReps(e.target.value)}
          inputMode="numeric"
          placeholder="reps"
          className="ck-field w-14 shrink-0 py-2.5 text-center text-sm sm:w-16"
        />
        <button
          onClick={logSet}
          disabled={busy || done >= target}
          className="ck-btn ck-btn-primary min-w-0 flex-1 py-2.5"
        >
          {done >= target ? "Done" : "Log Set"}
        </button>
      </div>

      <div className="mt-2">
        <input
          ref={videoRef}
          type="file"
          accept="video/*"
          capture="environment"
          className="hidden"
          onChange={(e) => onVideoPicked(e.target.files?.[0] ?? null)}
        />
        <button
          type="button"
          disabled={formBusy}
          onClick={() => videoRef.current?.click()}
          className="ck-btn ck-btn-ghost w-full py-2 text-xs"
        >
          {formBusy ? "Reading your set…" : "Check form (video)"}
        </button>
        {formErr && <p className="mt-1.5 text-[11px] text-brand">{formErr}</p>}
        {formResult && (
          <div className="mt-2 border border-line bg-paper p-3 animate-rise">
            <p className="ck-eyebrow">Form check</p>
            <p className="mt-1 text-sm leading-snug">{formResult.summary}</p>
            {formResult.looking_good?.length > 0 && (
              <div className="mt-2">
                <p className="text-[10px] font-semibold uppercase tracking-wider text-emerald-700/90">
                  Looking good
                </p>
                <ul className="mt-1 space-y-1 text-xs text-mut">
                  {formResult.looking_good.map((g) => (
                    <li key={g}>· {g}</li>
                  ))}
                </ul>
              </div>
            )}
            {formResult.cues?.length > 0 && (
              <div className="mt-2">
                <p className="text-[10px] font-semibold uppercase tracking-wider text-brand">
                  Next-set cues
                </p>
                <ul className="mt-1 space-y-1 text-xs text-fg-dim">
                  {formResult.cues.map((c) => (
                    <li key={c}>· {c}</li>
                  ))}
                </ul>
              </div>
            )}
            {formResult.safety_flags?.length > 0 && (
              <div className="mt-2 border border-brand bg-brand/5 p-2">
                <p className="text-[10px] font-semibold uppercase tracking-wider text-brand">
                  Watch
                </p>
                <ul className="mt-1 space-y-1 text-xs text-fg-dim">
                  {formResult.safety_flags.map((f) => (
                    <li key={f}>· {f}</li>
                  ))}
                </ul>
              </div>
            )}
            {formResult.unclear && (
              <p className="mt-2 text-[11px] text-mut">
                Film was unclear — try a side angle with the full bar path in frame.
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function InjuryProtocolCard({
  protocol,
  busy,
  onApply,
}: {
  protocol: InjuryProtocol;
  busy: boolean;
  onApply: (regionKey: string) => void;
}) {
  return (
    <div className="ck-cue mb-3">
      <p className="ck-cue-label">Protocol</p>
      <p className="mt-1 font-display text-lg font-black tracking-tight">{protocol.region}</p>
      {protocol.volume_hint && (
        <p className="mt-1 text-xs text-white/80">{protocol.volume_hint}</p>
      )}
      <ul className="mt-3 space-y-1.5 text-xs leading-snug text-white/90">
        {protocol.steps.map((step) => (
          <li key={step} className="flex gap-2">
            <span className="mt-1.5 h-1 w-1 shrink-0 bg-white" />
            <span>{step}</span>
          </li>
        ))}
      </ul>
      {protocol.alternatives.length > 0 && (
        <>
          <p className="mt-3 text-[11px] font-semibold uppercase tracking-wider text-white/70">
            Prefer today
          </p>
          <div className="mt-1.5 flex flex-wrap gap-1.5">
            {protocol.alternatives.map((alt) => (
              <span
                key={alt}
                className="border border-white/40 px-2 py-1 text-[11px] font-medium"
              >
                {alt}
              </span>
            ))}
          </div>
        </>
      )}
      <button
        type="button"
        disabled={busy}
        onClick={() => onApply(protocol.region_key)}
        className="ck-btn mt-3 w-full border border-white bg-white py-2.5 text-xs text-brand hover:bg-paper"
      >
        Apply suggested swaps
      </button>
    </div>
  );
}

function PainReport({
  options,
  onLogged,
}: {
  options: { key: string; label: string }[];
  onLogged: () => void;
}) {
  const [open, setOpen] = useState(false);
  const [busy, setBusy] = useState(false);

  async function logRegion(key: string) {
    setBusy(true);
    await api("/api/today/pain", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ region: key, severity: 5 }),
    });
    setBusy(false);
    setOpen(false);
    onLogged();
  }

  if (!options.length) return null;

  return (
    <div className="mb-4">
      {!open ? (
        <button
          type="button"
          onClick={() => setOpen(true)}
          className="text-[11px] font-semibold text-mut underline-offset-2 hover:text-brand hover:underline"
        >
          Something hurts? Flag a region
        </button>
      ) : (
        <div className="ck-surface border border-line p-3">
          <div className="flex items-center justify-between gap-2">
            <p className="text-xs font-semibold">Where&apos;s the pain?</p>
            <button
              type="button"
              onClick={() => setOpen(false)}
              className="text-[11px] text-mut hover:text-brand"
            >
              Cancel
            </button>
          </div>
          <div className="mt-2 flex flex-wrap gap-1.5">
            {options.map((o) => (
              <button
                key={o.key}
                type="button"
                disabled={busy}
                onClick={() => logRegion(o.key)}
                className="rounded-lg border border-line bg-paper px-2.5 py-1.5 text-[11px] font-semibold hover:border-brand disabled:opacity-40"
              >
                {o.label}
              </button>
            ))}
          </div>
          <p className="mt-2 text-[10px] text-mut">
            Sharp joint pain = stop. This opens a protocol card and suggests swaps.
          </p>
        </div>
      )}
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
    <div className="mb-5 border border-brand bg-panel p-4">
      <p className="font-display text-xs font-semibold tracking-[0.25em] text-brand">CHECK-IN</p>
      <span className="ck-signal-sm mt-2 max-w-[3rem]" />
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
              className="ck-field py-2 text-center text-sm"
            />
          </label>
        ))}
      </div>
      <button
        onClick={submit}
        disabled={busy}
        className="ck-btn ck-btn-primary mt-4 w-full disabled:opacity-40"
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
  const [restFor, setRestFor] = useState<number | null>(null);
  const [protocolBusy, setProtocolBusy] = useState(false);
  const [shareMsg, setShareMsg] = useState("");
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
    if (r.ok) {
      const ex = plan.exercises[slot];
      const rest = typeof ex?.rest_s === "number" && ex.rest_s > 0 ? ex.rest_s : 90;
      setRestFor(rest);
      await load();
    }
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

  async function applyProtocol(regionKey: string) {
    if (!plan) return;
    setProtocolBusy(true);
    await api("/api/today/apply-protocol-swaps", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        program_id: plan.program_id,
        day_index: plan.day_index,
        region_key: regionKey,
      }),
    });
    setProtocolBusy(false);
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
        <div className="absolute inset-0 bg-gradient-to-t from-brand via-brand/80 to-ink/45" />
        <div className="relative animate-rise text-left">
          <p className="font-display text-xs font-extrabold tracking-[0.32em] text-white">TODAY</p>
          <span className="mt-3 block h-0.5 w-16 bg-white" />
          <p className="mt-4 font-display text-2xl font-black tracking-tight text-white">No active program yet.</p>
          <p className="mt-2 max-w-sm text-sm text-white/85">
            Pick a book-inspired plan or ask Coach K to build one around your goals.
          </p>
          <button
            onClick={onGoToTemplates}
            className="ck-btn mt-6 bg-white text-brand hover:bg-paper"
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
        <div className="absolute inset-0 bg-gradient-to-t from-brand via-brand/85 to-ink/50" />
        <div className="relative animate-rise max-w-md text-left">
          <p className="font-display text-xs font-extrabold tracking-[0.32em] text-white">SESSION</p>
          <span className="mt-3 block h-0.5 w-16 bg-white" />
          <p className="mt-4 font-display text-2xl font-black tracking-tight text-white">
            {debrief?.headline ?? "Day complete — nice work."}
          </p>
          {debrief?.message && (
            <p className="mt-4 whitespace-pre-line text-sm leading-relaxed text-white/90">
              {debrief.message.replace(/\*\*/g, "")}
            </p>
          )}
          <div className="mt-6 flex flex-wrap items-center justify-center gap-2">
            <button
              type="button"
              onClick={async () => {
                const payload = formatSessionShare({
                  day_label: plan?.day_label,
                  focus: plan?.focus,
                  program_name: plan?.program_name,
                  exercises: plan?.exercises,
                  debrief,
                });
                const result = await shareContent(payload);
                setShareMsg(
                  result === "shared"
                    ? "Shared."
                    : result === "copied"
                      ? "Copied to clipboard."
                      : "Couldn't share — copy manually from the debrief.",
                );
              }}
              className="ck-btn ck-btn-primary"
            >
              Share session
            </button>
            <button
              type="button"
              onClick={() => {
                setFinished(false);
                setDebrief(null);
                setShareMsg("");
                setLoading(true);
                load();
              }}
              className="ck-btn ck-btn-ghost"
            >
              See what&apos;s next →
            </button>
          </div>
          {shareMsg && <p className="mt-3 text-xs text-mut">{shareMsg}</p>}
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
        <div className="mb-4 border border-line bg-panel p-4">
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
                className="border border-line px-3 py-1.5 text-xs font-semibold hover:border-brand"
              >
                {o.label}
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="mb-5 flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="font-display text-[11px] font-bold uppercase tracking-[0.28em] text-brand">Today</p>
          <h2 className="mt-1 font-display text-2xl font-black tracking-tight sm:text-3xl">{plan.day_label}</h2>
          <span className="ck-signal mt-2 max-w-[8rem]" />
          <p className="mt-2 text-sm text-mut">{plan.focus}</p>
          {plan.goal_mode && (
            <p className="mt-0.5 text-[11px] font-semibold uppercase tracking-wider text-brand">
              {plan.goal_mode} mode
            </p>
          )}
        </div>
        {getSpeechRecognition() && (
          <button
            onClick={startVoice}
            className={`h-11 w-11 shrink-0 text-lg ${
              listening ? "animate-pulse bg-brand text-white" : "border border-ink hover:border-brand"
            }`}
            title="Log a set by voice"
          >
            🎤
          </button>
        )}
      </div>

      {adapt && !needsCheckin && (
        <div className={`mb-4 border p-3 text-sm ${
          adapt.soft_day ? "border-brand bg-brand/5" : "border-line bg-panel"
        }`}>
          <p className="font-semibold capitalize">
            Readiness: {adapt.status}
            {adapt.score != null ? ` · ${adapt.score}` : ""}
            {adapt.soft_day ? " · soft day" : ""}
          </p>
          <p className="mt-1 text-xs text-mut">{adapt.intensity_note}</p>
          {adapt.reasons?.[0] && (
            <p className="mt-1 text-xs text-mut">{adapt.reasons[0]}</p>
          )}
        </div>
      )}

      {(plan.injury_protocols?.length ?? 0) > 0 && (
        <div className="mb-2 animate-rise">
          {plan.injury_protocols!.map((p) => (
            <InjuryProtocolCard
              key={p.region_key}
              protocol={p}
              busy={protocolBusy}
              onApply={applyProtocol}
            />
          ))}
        </div>
      )}

      <PainReport
        options={plan.pain_region_options ?? []}
        onLogged={load}
      />

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

      <div>
        {plan.exercises.map((ex, i) => (
          <ExerciseCard key={`${ex.exercise}-${i}`} ex={ex} slot={i} onLog={logSet} onSwap={swap} />
        ))}
      </div>

      <button
        onClick={finishWorkout}
        className="ck-btn ck-btn-primary mt-5 w-full py-3"
      >
        {allDone ? "Finish Workout" : "Finish Workout Anyway"}
      </button>

      {restFor != null && (
        <RestTimer
          seconds={restFor}
          onDone={() => setRestFor(null)}
          onDismiss={() => setRestFor(null)}
        />
      )}
    </div>
  );
}

/**
 * Mesocycle calendar — week view of training days, rest/travel/game markers.
 * One job: see the block ahead and mark real-life constraints.
 */

import { useEffect, useMemo, useState } from "react";
import { api } from "./api";

type TrainingInfo = {
  program_day_index: number;
  day_label: string;
  focus: string;
  exercises: number;
};

type CalDay = {
  date: string;
  weekday: string;
  is_today: boolean;
  kind: string;
  note?: string | null;
  training: TrainingInfo | null;
  completed: boolean;
};

type CalendarData = {
  start: string;
  end: string;
  weeks: number;
  program: {
    id: string;
    name: string;
    goal?: string;
    days_in_rotation: number;
    day_index: number;
    cycle_count: number;
    days_per_week: number;
  } | null;
  days: CalDay[];
};

const KIND_STYLE: Record<string, string> = {
  training: "border-brand/50 bg-brand/10",
  rest: "border-line bg-panel/40",
  travel: "border-sky-500/40 bg-sky-500/10",
  game: "border-amber-400/40 bg-amber-400/10",
  missed: "border-line/50 bg-paper opacity-70",
  completed: "border-emerald-500/30 bg-emerald-50",
  empty: "border-line/40 bg-transparent",
};

const KIND_LABEL: Record<string, string> = {
  training: "Train",
  rest: "Rest",
  travel: "Travel",
  game: "Game",
  missed: "Missed",
  completed: "Logged",
  empty: "—",
};

export default function Calendar({ onOpenToday }: { onOpenToday?: () => void }) {
  const [data, setData] = useState<CalendarData | null>(null);
  const [weeks, setWeeks] = useState(2);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<CalDay | null>(null);
  const [busy, setBusy] = useState(false);

  const load = () => {
    setLoading(true);
    api(`/api/calendar?weeks=${weeks}`)
      .then((r) => (r.ok ? r.json() : null))
      .then((d) => {
        setData(d);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [weeks]);

  const weeksGrid = useMemo(() => {
    if (!data) return [];
    const out: CalDay[][] = [];
    for (let i = 0; i < data.days.length; i += 7) {
      out.push(data.days.slice(i, i + 7));
    }
    return out;
  }, [data]);

  async function setMarker(kind: string | null) {
    if (!selected) return;
    setBusy(true);
    await api("/api/calendar/marker", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ date: selected.date, kind }),
    });
    setBusy(false);
    setSelected(null);
    load();
  }

  async function jumpToDay(programId: string, dayIndex: number) {
    setBusy(true);
    await api("/api/calendar/jump", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ program_id: programId, day_index: dayIndex }),
    });
    setBusy(false);
    setSelected(null);
    onOpenToday?.();
  }

  if (loading && !data) return <div className="flex-1" />;

  return (
    <div className="mx-auto w-full max-w-3xl flex-1 overflow-y-auto px-4 py-5 pb-[calc(1.25rem+env(safe-area-inset-bottom))] sm:px-6 sm:py-6">
      <div className="animate-fade">
        <p className="ck-eyebrow">Calendar</p>
        <div className="mt-2 flex flex-wrap items-end justify-between gap-3">
          <div>
            <h1 className="font-display text-3xl font-black tracking-tight">The block ahead.</h1>
            <p className="mt-1 text-sm text-mut">
              {data?.program
                ? `${data.program.name} · ${data.program.days_per_week} days/wk · cycle ${data.program.cycle_count + 1}`
                : "No active program — mark rest/travel anyway, or start a plan."}
            </p>
          </div>
          <div className="flex gap-1 rounded-xl border border-line bg-panel/50 p-0.5">
            {[1, 2, 4].map((w) => (
              <button
                key={w}
                onClick={() => setWeeks(w)}
                className={`rounded-lg px-2.5 py-1.5 text-xs font-semibold ${
                  weeks === w ? "bg-brand text-white" : "text-mut hover:text-brand"
                }`}
              >
                {w}w
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="mt-4 flex flex-wrap gap-3 text-[11px] text-mut">
        {[
          ["training", "Training"],
          ["rest", "Rest"],
          ["travel", "Travel"],
          ["game", "Game / event"],
        ].map(([k, label]) => (
          <span key={k} className="inline-flex items-center gap-1.5">
            <span className={`h-2.5 w-2.5 rounded-sm border ${KIND_STYLE[k]}`} />
            {label}
          </span>
        ))}
      </div>

      <div className="mt-6 space-y-6">
        {weeksGrid.map((week, wi) => (
          <section key={wi} className="animate-rise">
            <p className="mb-2 text-[11px] font-semibold uppercase tracking-wider text-mut">
              Week of {week[0]?.date}
            </p>
            <div className="grid grid-cols-7 gap-1.5 sm:gap-2">
              {week.map((d) => {
                const style = KIND_STYLE[d.kind] || KIND_STYLE.empty;
                return (
                  <button
                    key={d.date}
                    type="button"
                    onClick={() => setSelected(d)}
                    className={`min-h-[4.5rem] rounded-xl border p-1.5 text-left transition hover:border-brand sm:min-h-[5.5rem] sm:p-2 ${style} ${
                      d.is_today ? "ring-1 ring-brand" : ""
                    }`}
                  >
                    <div className="flex items-baseline justify-between gap-0.5">
                      <span className="text-[10px] font-semibold text-mut">{d.weekday}</span>
                      <span className={`text-[11px] tabular-nums ${d.is_today ? "font-bold text-brand" : "text-mut"}`}>
                        {d.date.slice(8)}
                      </span>
                    </div>
                    <p className="mt-1 line-clamp-2 text-[10px] font-semibold leading-snug sm:text-[11px]">
                      {d.training?.day_label
                        ? d.training.day_label.replace(/^Day\s*\d+\s*[—–-]?\s*/i, "") || d.training.day_label
                        : KIND_LABEL[d.kind]}
                    </p>
                    {d.completed && (
                      <p className="mt-0.5 text-[9px] font-semibold text-emerald-700">Done</p>
                    )}
                  </button>
                );
              })}
            </div>
          </section>
        ))}
      </div>

      {selected && (
        <div
          className="fixed inset-0 z-40 flex items-end justify-center bg-ink/40 p-0 sm:items-center sm:p-4"
          onClick={() => setSelected(null)}
        >
          <div
            className="ck-surface-elevated w-full max-w-md rounded-t-2xl p-5 pb-[calc(1.25rem+env(safe-area-inset-bottom))] sm:rounded-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <p className="ck-eyebrow">{selected.weekday} · {selected.date}</p>
            <h2 className="mt-2 font-display text-xl font-black">
              {selected.training?.day_label || KIND_LABEL[selected.kind]}
            </h2>
            {selected.training?.focus && (
              <p className="mt-1 text-sm text-mut">{selected.training.focus}</p>
            )}
            {selected.training && (
              <p className="mt-1 text-xs text-mut">{selected.training.exercises} exercises</p>
            )}
            {selected.note && <p className="mt-2 text-sm text-fg-dim">{selected.note}</p>}

            <p className="mt-5 text-[11px] font-semibold uppercase tracking-wider text-mut">
              Mark this day
            </p>
            <div className="mt-2 grid grid-cols-2 gap-2">
              {(
                [
                  ["rest", "Rest day"],
                  ["travel", "Travel"],
                  ["game", "Game / event"],
                  [null, "Clear marker"],
                ] as const
              ).map(([kind, label]) => (
                <button
                  key={label}
                  type="button"
                  disabled={busy}
                  onClick={() => setMarker(kind)}
                  className="ck-btn ck-btn-ghost py-2.5 text-xs"
                >
                  {label}
                </button>
              ))}
            </div>

            {selected.is_today && selected.kind === "training" && (
              <button
                type="button"
                className="ck-btn ck-btn-primary mt-4 w-full"
                onClick={() => onOpenToday?.()}
              >
                Open Today's workout
              </button>
            )}

            {selected.training && data?.program && !selected.is_today && (
              <button
                type="button"
                disabled={busy}
                className="ck-btn ck-btn-ghost mt-3 w-full"
                onClick={() => jumpToDay(data.program!.id, selected.training!.program_day_index)}
              >
                Jump rotation to this day
              </button>
            )}

            <button
              type="button"
              className="mt-3 w-full py-2 text-sm text-mut hover:text-brand"
              onClick={() => setSelected(null)}
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

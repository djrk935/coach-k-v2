/**
 * Progress dashboard — one job per section, brand-aligned SVG charts.
 * e1RM trends · bodyweight · readiness · training load / ACWR · recent PRs
 */

import { useEffect, useMemo, useState, type ReactNode } from "react";
import { api } from "./api";

type Point = { date: string; value: number };
type LiftSeries = {
  points: { date: string; e1rm: number }[];
  current: number;
  delta: number;
  delta_pct: number;
};
type ProgressData = {
  days: number;
  lifts: Record<string, LiftSeries>;
  bodyweight: { date: string; lbs: number }[];
  readiness: { date: string; score: number }[];
  load: { date: string; load: number }[];
  acwr_series: { date: string; acwr: number }[];
  load_summary: { acwr: number | null; sessions_28d: number; load_note?: string };
  prs: { date: string; exercise: string; weight_lbs: number | null; reps: number | null }[];
  sessions: number;
  profile_1rms: Record<string, number>;
  goal_mode?: string;
};

const LIFT_LABELS: Record<string, string> = {
  squat: "Squat",
  bench: "Bench",
  deadlift: "Deadlift",
  press: "Press",
};

function Sparkline({
  points,
  color = "#e11d2e",
  height = 72,
  fill = true,
}: {
  points: Point[];
  color?: string;
  height?: number;
  fill?: boolean;
}) {
  const width = 320;
  const pad = 6;
  const path = useMemo(() => {
    if (points.length < 2) return null;
    const vals = points.map((p) => p.value);
    const min = Math.min(...vals);
    const max = Math.max(...vals);
    const span = max - min || 1;
    const coords = points.map((p, i) => {
      const x = pad + (i / (points.length - 1)) * (width - pad * 2);
      const y = pad + (1 - (p.value - min) / span) * (height - pad * 2);
      return [x, y] as const;
    });
    const line = coords.map((c, i) => `${i === 0 ? "M" : "L"}${c[0].toFixed(1)},${c[1].toFixed(1)}`).join(" ");
    const area =
      line +
      ` L${coords[coords.length - 1][0].toFixed(1)},${height - pad}` +
      ` L${coords[0][0].toFixed(1)},${height - pad} Z`;
    return { line, area, last: coords[coords.length - 1] };
  }, [points, height]);

  if (!path) {
    return (
      <div className="flex h-[72px] items-center text-xs text-mut">
        {points.length === 1 ? "One data point — keep logging." : "No data yet."}
      </div>
    );
  }

  return (
    <svg viewBox={`0 0 ${width} ${height}`} className="h-[72px] w-full" preserveAspectRatio="none">
      {fill && <path d={path.area} fill={color} opacity="0.12" />}
      <path d={path.line} fill="none" stroke={color} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
      <circle cx={path.last[0]} cy={path.last[1]} r="3.5" fill={color} />
    </svg>
  );
}

function StatCard({
  label,
  value,
  hint,
  children,
}: {
  label: string;
  value: string;
  hint?: string;
  children?: ReactNode;
}) {
  return (
    <section className="ck-surface overflow-hidden p-4">
      <div className="flex items-baseline justify-between gap-2">
        <p className="ck-eyebrow !tracking-[0.22em]">{label}</p>
        {hint && <p className="text-[11px] text-mut">{hint}</p>}
      </div>
      <p className="mt-2 font-display text-2xl font-black tracking-tight tabular-nums">{value}</p>
      <div className="mt-3">{children}</div>
    </section>
  );
}

export default function Progress() {
  const [data, setData] = useState<ProgressData | null>(null);
  const [days, setDays] = useState(90);
  const [loading, setLoading] = useState(true);
  const [liftKey, setLiftKey] = useState<string>("squat");

  useEffect(() => {
    setLoading(true);
    api(`/api/progress?days=${days}`)
      .then((r) => (r.ok ? r.json() : null))
      .then((d) => {
        setData(d);
        if (d?.lifts) {
          const keys = Object.keys(d.lifts);
          if (keys.length && !d.lifts[liftKey]) setLiftKey(keys[0]);
        }
        setLoading(false);
      })
      .catch(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [days]);

  if (loading && !data) {
    return <div className="flex-1" />;
  }

  if (!data || (data.sessions === 0 && !Object.keys(data.lifts).length && !data.bodyweight.length)) {
    return (
      <div className="relative flex flex-1 flex-col items-center justify-center overflow-hidden px-6 text-center">
        <img src="/images/atmosphere-kettle.jpg" alt="" className="absolute inset-0 h-full w-full object-cover opacity-30" />
        <div className="absolute inset-0 bg-gradient-to-t from-ink via-ink/85 to-ink/50" />
        <div className="relative animate-rise max-w-sm">
          <p className="ck-eyebrow">Progress</p>
          <h2 className="mt-3 font-display text-2xl font-black tracking-tight">
            Log sessions to unlock your chart.
          </h2>
          <p className="mt-2 text-sm text-mut">
            e1RM trends, bodyweight, readiness, and load appear here once you train and check in.
          </p>
        </div>
      </div>
    );
  }

  const liftKeys = Object.keys(data.lifts);
  const activeLift = data.lifts[liftKey] || data.lifts[liftKeys[0]];
  const bwPoints: Point[] = data.bodyweight.map((p) => ({ date: p.date, value: p.lbs }));
  const readyPoints: Point[] = data.readiness.map((p) => ({ date: p.date, value: p.score }));
  const loadPoints: Point[] = data.load.map((p) => ({ date: p.date, value: p.load }));
  const acwrPoints: Point[] = data.acwr_series.map((p) => ({ date: p.date, value: p.acwr }));
  const acwrNow = data.load_summary?.acwr;

  const bwDelta =
    bwPoints.length >= 2
      ? round1(bwPoints[bwPoints.length - 1].value - bwPoints[0].value)
      : null;

  return (
    <div className="mx-auto w-full max-w-3xl flex-1 overflow-y-auto px-4 py-5 pb-[calc(1.25rem+env(safe-area-inset-bottom))] sm:px-6 sm:py-6">
      <div className="animate-fade">
        <p className="ck-eyebrow">Progress</p>
        <div className="mt-2 flex flex-wrap items-end justify-between gap-3">
          <div>
            <h1 className="font-display text-3xl font-black tracking-tight">Your numbers.</h1>
            <p className="mt-1 text-sm text-mut">
              {data.sessions} sessions · last {days} days
              {data.goal_mode ? ` · ${data.goal_mode}` : ""}
            </p>
          </div>
          <div className="flex gap-1 rounded-xl border border-line bg-panel/50 p-0.5">
            {[30, 90, 180].map((d) => (
              <button
                key={d}
                onClick={() => setDays(d)}
                className={`rounded-lg px-2.5 py-1.5 text-xs font-semibold ${
                  days === d ? "bg-brand text-white" : "text-mut hover:text-white"
                }`}
              >
                {d}d
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Strength — one section */}
      <section className="mt-8 animate-rise">
        <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
          <h2 className="font-display text-lg font-bold">Estimated 1RM</h2>
          {liftKeys.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {liftKeys.map((k) => (
                <button
                  key={k}
                  onClick={() => setLiftKey(k)}
                  className={`rounded-lg px-2.5 py-1 text-[11px] font-semibold capitalize ${
                    liftKey === k ? "bg-brand text-white" : "border border-line text-mut hover:text-white"
                  }`}
                >
                  {LIFT_LABELS[k] || k}
                </button>
              ))}
            </div>
          )}
        </div>
        {activeLift ? (
          <StatCard
            label={LIFT_LABELS[liftKey] || liftKey}
            value={`${fmt(activeLift.current)} lbs`}
            hint={
              activeLift.delta !== 0
                ? `${activeLift.delta > 0 ? "+" : ""}${fmt(activeLift.delta)} lbs (${activeLift.delta_pct > 0 ? "+" : ""}${activeLift.delta_pct}%)`
                : "Holding steady"
            }
          >
            <Sparkline
              points={activeLift.points.map((p) => ({ date: p.date, value: p.e1rm }))}
            />
          </StatCard>
        ) : (
          <div className="ck-surface p-4 text-sm text-mut">
            No squat/bench/deadlift/press sets logged yet. Profile 1RMs:{" "}
            {Object.keys(data.profile_1rms).length
              ? Object.entries(data.profile_1rms)
                  .map(([k, v]) => `${k} ${v}`)
                  .join(" · ")
              : "none set"}
          </div>
        )}

        {liftKeys.length > 1 && (
          <div className="mt-3 grid grid-cols-2 gap-2 sm:grid-cols-4">
            {liftKeys.map((k) => {
              const L = data.lifts[k];
              return (
                <button
                  key={k}
                  onClick={() => setLiftKey(k)}
                  className={`ck-surface p-3 text-left transition hover:border-brand ${
                    liftKey === k ? "border-brand" : ""
                  }`}
                >
                  <p className="text-[10px] font-semibold uppercase tracking-wider text-mut">
                    {LIFT_LABELS[k] || k}
                  </p>
                  <p className="mt-1 font-display text-lg font-black tabular-nums">{fmt(L.current)}</p>
                  <p className={`text-[11px] ${L.delta >= 0 ? "text-emerald-400" : "text-brand"}`}>
                    {L.delta >= 0 ? "+" : ""}
                    {fmt(L.delta)}
                  </p>
                </button>
              );
            })}
          </div>
        )}
      </section>

      {/* Body + readiness */}
      <section className="mt-8 grid gap-3 sm:grid-cols-2">
        <StatCard
          label="Bodyweight"
          value={bwPoints.length ? `${fmt(bwPoints[bwPoints.length - 1].value)} lbs` : "—"}
          hint={bwDelta != null ? `${bwDelta > 0 ? "+" : ""}${bwDelta} lbs in window` : undefined}
        >
          <Sparkline points={bwPoints} color="#c4c4cc" />
        </StatCard>
        <StatCard
          label="Readiness"
          value={
            readyPoints.length
              ? String(Math.round(readyPoints[readyPoints.length - 1].value))
              : "—"
          }
          hint="Check-ins + HealthKit"
        >
          <Sparkline points={readyPoints} color="#34d399" />
        </StatCard>
      </section>

      {/* Load */}
      <section className="mt-8 animate-rise delay-75">
        <h2 className="mb-3 font-display text-lg font-bold">Training load</h2>
        <div className="grid gap-3 sm:grid-cols-2">
          <StatCard
            label="Session load"
            value={loadPoints.length ? fmt(loadPoints[loadPoints.length - 1].value) : "—"}
            hint={`${data.load_summary?.sessions_28d ?? 0} sessions / 28d`}
          >
            <Sparkline points={loadPoints} color="#f59e0b" />
          </StatCard>
          <StatCard
            label="ACWR"
            value={acwrNow != null ? String(acwrNow) : "—"}
            hint={
              acwrNow == null
                ? data.load_summary?.load_note || "Building baseline"
                : acwrNow > 1.5
                  ? "Spike — ease up"
                  : acwrNow > 1.3
                    ? "Elevated"
                    : "In the zone"
            }
          >
            <Sparkline points={acwrPoints} color="#e11d2e" fill={false} />
          </StatCard>
        </div>
      </section>

      {/* PRs */}
      <section className="mt-8 animate-rise delay-150">
        <h2 className="mb-3 font-display text-lg font-bold">Recent PRs</h2>
        {data.prs.length === 0 ? (
          <div className="ck-surface p-4 text-sm text-mut">No PRs in this window yet — they show up when you beat prior e1RM.</div>
        ) : (
          <ul className="ck-surface divide-y divide-line/80">
            {data.prs.map((pr, i) => (
              <li key={`${pr.date}-${pr.exercise}-${i}`} className="flex items-center justify-between gap-3 px-4 py-3">
                <div className="min-w-0">
                  <p className="truncate font-semibold">{pr.exercise}</p>
                  <p className="text-xs text-mut">{pr.date}</p>
                </div>
                <p className="shrink-0 font-display font-bold tabular-nums text-brand">
                  {pr.weight_lbs ?? "—"}×{pr.reps ?? "—"}
                </p>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}

function fmt(n: number) {
  return Number.isInteger(n) ? String(n) : n.toFixed(1);
}
function round1(n: number) {
  return Math.round(n * 10) / 10;
}

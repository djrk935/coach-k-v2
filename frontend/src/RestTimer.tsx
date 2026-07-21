/** Circular rest timer — Signal Strip bar after logging a set. */

import { useEffect, useState } from "react";

type Props = {
  seconds?: number;
  onDone?: () => void;
  onDismiss?: () => void;
};

export default function RestTimer({ seconds = 90, onDone, onDismiss }: Props) {
  const [left, setLeft] = useState(seconds);
  const total = seconds;
  const pct = left / total;
  const r = 45;
  const c = 2 * Math.PI * r;
  const offset = c * (1 - pct);
  const overdue = left <= 0;

  useEffect(() => {
    setLeft(seconds);
  }, [seconds]);

  useEffect(() => {
    if (left <= 0) {
      onDone?.();
      return;
    }
    const t = setTimeout(() => setLeft((x) => x - 1), 1000);
    return () => clearTimeout(t);
  }, [left, onDone]);

  const mm = String(Math.floor(left / 60)).padStart(1, "0");
  const ss = String(left % 60).padStart(2, "0");

  return (
    <div className="fixed inset-x-0 bottom-0 z-40 flex justify-center pb-[calc(1rem+env(safe-area-inset-bottom))] pt-2">
      <div className="mx-4 flex w-full max-w-sm items-center gap-4 border border-brand bg-white px-4 py-3 shadow-sm">
        <div className="relative h-16 w-16 shrink-0">
          <svg viewBox="0 0 100 100" className="h-full w-full rest-ring">
            <circle cx="50" cy="50" r={r} fill="none" stroke="#e4dfdf" strokeWidth="8" />
            <circle
              cx="50"
              cy="50"
              r={r}
              fill="none"
              stroke="#e11d2e"
              strokeWidth="8"
              strokeLinecap="butt"
              strokeDasharray={c}
              strokeDashoffset={offset}
              style={{ transition: "stroke-dashoffset 0.9s linear" }}
            />
          </svg>
          <span className="absolute inset-0 flex items-center justify-center font-display text-sm font-bold tabular-nums text-brand">
            {mm}:{ss}
          </span>
        </div>
        <div className="min-w-0 flex-1">
          <p className="font-display text-sm font-bold uppercase tracking-wider text-brand">
            {overdue ? "Rest due" : "Rest"}
          </p>
          <p className="text-xs text-mut">Breathe. Next set when the ring closes.</p>
        </div>
        <button
          type="button"
          onClick={onDismiss}
          className="ck-btn ck-btn-ghost px-3 py-2 text-xs"
        >
          Skip
        </button>
      </div>
    </div>
  );
}

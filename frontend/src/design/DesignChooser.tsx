/**
 * UI direction chooser — four full mockups for Dayan to pick from.
 * Open with ?design=1 (no password). Pick one; we implement that system next.
 */

import { useEffect, useState } from "react";

export type DirectionId = "iron-forge" | "day-court" | "film-cut" | "signal-strip";

type Direction = {
  id: DirectionId;
  name: string;
  tagline: string;
  vibe: string;
  fonts: string;
  palette: string[];
};

const DIRECTIONS: Direction[] = [
  {
    id: "iron-forge",
    name: "Iron Forge",
    tagline: "Dark gym. Signal red. Coach-first.",
    vibe: "Closest to today’s DNA, but cleaner hierarchy and stronger brand presence.",
    fonts: "Syne + Manrope",
    palette: ["#09090b", "#e11d2e", "#f0f0f3", "#2c2c34"],
  },
  {
    id: "day-court",
    name: "Day Court",
    tagline: "Daylight athletics. Chalk and green.",
    vibe: "Bright training floor energy — readable outdoors, still branded for Dayan.",
    fonts: "Archivo Black + Outfit",
    palette: ["#f3f1ec", "#0f1410", "#1f7a4c", "#c45c26"],
  },
  {
    id: "film-cut",
    name: "Film Cut",
    tagline: "Tungsten dark. Cinematic stills.",
    vibe: "Film-room coaching — warm light, deep blacks, image-led compositions.",
    fonts: "Space Grotesk + Figtree",
    palette: ["#0c0a09", "#e8b86d", "#f5f0e8", "#3d3429"],
  },
  {
    id: "signal-strip",
    name: "Signal Strip",
    tagline: "High contrast. Magazine athletics.",
    vibe: "Bold type, thin red rules, almost-poster energy without looking like a newspaper.",
    fonts: "Bebas Neue + Source Sans 3",
    palette: ["#ffffff", "#111111", "#dc2626", "#e5e5e5"],
  },
];

function MockPhone({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return (
    <div
      className={`relative mx-auto w-full max-w-[390px] overflow-hidden rounded-[2rem] border shadow-2xl ${className}`}
      style={{ aspectRatio: "390 / 780" }}
    >
      {children}
    </div>
  );
}

function NavDots({ active }: { active: string }) {
  return (
    <div className="flex gap-4 text-[10px] font-semibold uppercase tracking-wider opacity-70">
      {["today", "chat", "plans", "stats"].map((t) => (
        <span key={t} className={t === active ? "opacity-100 underline underline-offset-4" : ""}>
          {t}
        </span>
      ))}
    </div>
  );
}

/** 1 — Iron Forge */
function IronForgePreview() {
  return (
    <MockPhone className="border-zinc-700 bg-[#09090b] text-[#f0f0f3]">
      <div className="absolute inset-0">
        <img src="/images/training-floor.jpg" alt="" className="h-[58%] w-full object-cover" />
        <div className="absolute inset-x-0 top-0 h-[58%] bg-gradient-to-t from-[#09090b] via-[#09090b]/55 to-transparent" />
        <div className="absolute inset-x-0 bottom-0 h-[48%] bg-[#09090b]" />
      </div>
      <div className="relative flex h-full flex-col px-5 pb-6 pt-10" style={{ fontFamily: "Manrope, sans-serif" }}>
        <p
          className="text-[11px] font-extrabold tracking-[0.35em] text-[#e11d2e]"
          style={{ fontFamily: "Syne, sans-serif" }}
        >
          COACH K
        </p>
        <h1
          className="mt-3 max-w-[14ch] text-[2.15rem] font-black leading-[0.95] tracking-tight"
          style={{ fontFamily: "Syne, sans-serif" }}
        >
          Train with a coach who shows up.
        </h1>
        <p className="mt-3 max-w-[28ch] text-[13px] leading-relaxed text-white/70">
          Dayan Kijege — from the DRC to Austin. Programs that adapt to you.
        </p>
        <div className="mt-5 flex gap-2">
          <button className="rounded-xl bg-[#e11d2e] px-4 py-2.5 text-xs font-bold text-white">
            Enter Coach K
          </button>
          <button className="rounded-xl border border-white/25 px-4 py-2.5 text-xs font-semibold text-white/90">
            My story
          </button>
        </div>
        <div className="mt-auto rounded-2xl border border-[#2c2c34] bg-[#121216]/95 p-3 backdrop-blur">
          <NavDots active="today" />
          <p className="mt-3 text-[10px] font-bold uppercase tracking-[0.2em] text-[#e11d2e]">Today</p>
          <p className="mt-1 text-sm font-bold" style={{ fontFamily: "Syne, sans-serif" }}>
            Day 2 — Lower Strength
          </p>
          <p className="text-[11px] text-white/50">Soft day · volume trimmed · 4 lifts</p>
          <div className="mt-3 space-y-2">
            {["Back Squat · 4×5", "RDL · 3×8"].map((row) => (
              <div
                key={row}
                className="flex items-center justify-between rounded-xl border border-[#2c2c34] bg-[#09090b] px-3 py-2 text-[11px]"
              >
                <span>{row}</span>
                <span className="font-bold text-[#e11d2e]">Log</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </MockPhone>
  );
}

/** 2 — Day Court */
function DayCourtPreview() {
  return (
    <MockPhone className="border-[#d9d4cb] bg-[#f3f1ec] text-[#0f1410]">
      <div className="absolute inset-0">
        <img
          src="/images/chalk-hands.jpg"
          alt=""
          className="h-[52%] w-full object-cover brightness-110 contrast-105"
        />
        <div className="absolute inset-x-0 top-0 h-[52%] bg-gradient-to-t from-[#f3f1ec] via-[#f3f1ec]/40 to-transparent" />
      </div>
      <div className="relative flex h-full flex-col px-5 pb-6 pt-10" style={{ fontFamily: "Outfit, sans-serif" }}>
        <div className="flex items-center justify-between">
          <p
            className="text-[1.35rem] font-black uppercase tracking-tight text-[#0f1410]"
            style={{ fontFamily: "Archivo Black, sans-serif" }}
          >
            Coach K
          </p>
          <span className="rounded-full bg-[#1f7a4c] px-2.5 py-1 text-[10px] font-bold text-white">
            Live
          </span>
        </div>
        <h1
          className="mt-8 max-w-[12ch] text-[2.4rem] font-black uppercase leading-[0.9] tracking-tight"
          style={{ fontFamily: "Archivo Black, sans-serif" }}
        >
          Show up. Get scored. Get better.
        </h1>
        <p className="mt-4 max-w-[32ch] text-[13px] leading-relaxed text-[#0f1410]/70">
          Dayan’s court-to-weight-room system — readiness, load, and honest feedback.
        </p>
        <button className="mt-6 w-fit rounded-full bg-[#0f1410] px-5 py-3 text-xs font-bold text-[#f3f1ec]">
          Start today’s session
        </button>
        <div className="mt-auto space-y-2">
          <div className="rounded-2xl bg-white p-3 shadow-[0_12px_40px_rgba(15,20,16,0.08)]">
            <p className="text-[10px] font-bold uppercase tracking-[0.18em] text-[#1f7a4c]">Today · Lower</p>
            <div className="mt-2 flex items-end justify-between">
              <p className="text-lg font-bold" style={{ fontFamily: "Archivo Black, sans-serif" }}>
                Readiness 78
              </p>
              <p className="text-[11px] text-[#c45c26]">ACWR 1.12</p>
            </div>
            <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-[#e8e4dc]">
              <div className="h-full w-[78%] rounded-full bg-[#1f7a4c]" />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-2">
            {["Squat", "RDL"].map((x) => (
              <div key={x} className="rounded-2xl bg-[#0f1410] px-3 py-3 text-[#f3f1ec]">
                <p className="text-[10px] opacity-60">Working</p>
                <p className="text-sm font-bold">{x}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </MockPhone>
  );
}

/** 3 — Film Cut */
function FilmCutPreview() {
  return (
    <MockPhone className="border-[#3d3429] bg-[#0c0a09] text-[#f5f0e8]">
      <div className="absolute inset-0">
        <img
          src="/images/coach-dayan-speaking.jpg"
          alt=""
          className="h-full w-full object-cover object-[30%_20%] opacity-55"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-[#0c0a09] via-[#0c0a09]/75 to-[#0c0a09]/25" />
      </div>
      <div className="relative flex h-full flex-col px-5 pb-6 pt-10" style={{ fontFamily: "Figtree, sans-serif" }}>
        <p
          className="text-[11px] font-medium tracking-[0.28em] text-[#e8b86d]"
          style={{ fontFamily: "Space Grotesk, sans-serif" }}
        >
          COACH K · DAYAN
        </p>
        <div className="mt-auto">
          <h1
            className="max-w-[14ch] text-[2.35rem] font-medium leading-[1.02] tracking-[-0.03em]"
            style={{ fontFamily: "Space Grotesk, sans-serif" }}
          >
            The cut that makes athletes.
          </h1>
          <p className="mt-3 max-w-[30ch] text-[13px] leading-relaxed text-[#f5f0e8]/75">
            Science in the film room. Honest notes after every set.
          </p>
          <div className="mt-6 flex items-center gap-3">
            <button className="rounded-md bg-[#e8b86d] px-4 py-2.5 text-xs font-bold text-[#0c0a09]">
              Open session
            </button>
            <button className="text-xs font-semibold text-[#f5f0e8]/80 underline underline-offset-4">
              Watch story
            </button>
          </div>
          <div className="mt-8 border-t border-[#e8b86d]/25 pt-4">
            <div className="flex justify-between text-[10px] uppercase tracking-[0.2em] text-[#e8b86d]/80">
              <span>Day 2</span>
              <span>Soft day</span>
            </div>
            <p className="mt-2 text-sm font-medium" style={{ fontFamily: "Space Grotesk, sans-serif" }}>
              Lower · Strength bias
            </p>
            <div className="mt-3 flex gap-2 overflow-hidden">
              {["Setup", "Working", "Debrief"].map((s, i) => (
                <span
                  key={s}
                  className={`rounded-sm px-2 py-1 text-[10px] font-semibold ${
                    i === 1 ? "bg-[#e8b86d] text-[#0c0a09]" : "bg-white/10 text-white/70"
                  }`}
                >
                  {s}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </MockPhone>
  );
}

/** 4 — Signal Strip */
function SignalStripPreview() {
  return (
    <MockPhone className="border-neutral-300 bg-white text-[#111]">
      <div className="relative flex h-full flex-col" style={{ fontFamily: "Source Sans 3, sans-serif" }}>
        <div className="relative h-[46%] overflow-hidden">
          <img src="/images/hero-barbell.jpg" alt="" className="h-full w-full object-cover grayscale" />
          <div className="absolute inset-0 bg-black/35" />
          <div className="absolute left-0 top-0 h-full w-1.5 bg-[#dc2626]" />
          <div className="absolute bottom-4 left-5 right-5 text-white">
            <p
              className="text-[2.6rem] leading-none tracking-wide"
              style={{ fontFamily: "Bebas Neue, sans-serif" }}
            >
              COACH K
            </p>
            <p className="mt-1 text-[12px] font-semibold uppercase tracking-[0.18em] text-white/80">
              Dayan Kijege
            </p>
          </div>
        </div>
        <div className="flex flex-1 flex-col px-5 pb-6 pt-5">
          <h1
            className="text-[2.7rem] leading-[0.9] tracking-wide"
            style={{ fontFamily: "Bebas Neue, sans-serif" }}
          >
            NO FLUFF.
            <br />
            JUST THE WORK.
          </h1>
          <p className="mt-3 max-w-[34ch] text-[13px] leading-relaxed text-neutral-600">
            Periodized plans, readiness gates, and cues you can run tonight.
          </p>
          <div className="mt-5 h-px w-full bg-[#dc2626]" />
          <div className="mt-4 grid grid-cols-3 gap-2 text-center">
            {[
              ["78", "Ready"],
              ["1.1", "ACWR"],
              ["4", "Lifts"],
            ].map(([n, l]) => (
              <div key={l} className="border border-neutral-200 py-2">
                <p className="text-xl leading-none" style={{ fontFamily: "Bebas Neue, sans-serif" }}>
                  {n}
                </p>
                <p className="mt-1 text-[10px] font-bold uppercase tracking-wider text-neutral-500">{l}</p>
              </div>
            ))}
          </div>
          <button className="mt-auto w-full bg-[#111] py-3 text-xs font-bold uppercase tracking-[0.14em] text-white">
            Enter session →
          </button>
        </div>
      </div>
    </MockPhone>
  );
}

const PREVIEWS: Record<DirectionId, () => React.ReactElement> = {
  "iron-forge": IronForgePreview,
  "day-court": DayCourtPreview,
  "film-cut": FilmCutPreview,
  "signal-strip": SignalStripPreview,
};

export default function DesignChooser({
  onPick,
}: {
  onPick?: (id: DirectionId) => void;
}) {
  const [active, setActive] = useState<DirectionId>("iron-forge");
  const [picked, setPicked] = useState<DirectionId | null>(null);
  const Preview = PREVIEWS[active];
  const meta = DIRECTIONS.find((d) => d.id === active)!;

  useEffect(() => {
    document.documentElement.classList.toggle("design-day-court", active === "day-court");
    document.documentElement.classList.toggle("design-signal", active === "signal-strip");
    return () => {
      document.documentElement.classList.remove("design-day-court", "design-signal");
    };
  }, [active]);

  function choose() {
    setPicked(active);
    localStorage.setItem("coachk_ui_direction", active);
    onPick?.(active);
  }

  return (
    <div className="min-h-full overflow-y-auto bg-[#0a0a0c] text-white">
      <header className="border-b border-white/10 px-4 py-5 sm:px-8">
        <p className="text-[11px] font-bold uppercase tracking-[0.28em] text-[#e11d2e]">Coach K · UI directions</p>
        <h1 className="mt-2 font-display text-2xl font-black tracking-tight sm:text-3xl">
          Pick the look we build next.
        </h1>
        <p className="mt-2 max-w-2xl text-sm text-white/60">
          Four full directions — same product, different presence. Tap a card, preview the phone,
          then lock one in. We’ll rebuild Landing + Today + nav to match.
        </p>
      </header>

      <div className="mx-auto grid max-w-6xl gap-8 px-4 py-8 lg:grid-cols-[minmax(0,1fr)_400px] sm:px-8">
        <div className="space-y-3">
          {DIRECTIONS.map((d) => {
            const selected = active === d.id;
            return (
              <button
                key={d.id}
                type="button"
                onClick={() => setActive(d.id)}
                className={`w-full rounded-2xl border p-4 text-left transition ${
                  selected
                    ? "border-[#e11d2e] bg-[#e11d2e]/10"
                    : "border-white/10 bg-white/[0.03] hover:border-white/25"
                }`}
              >
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <p className="font-display text-lg font-black">{d.name}</p>
                    <p className="mt-0.5 text-sm text-white/70">{d.tagline}</p>
                  </div>
                  <div className="flex gap-1.5">
                    {d.palette.map((c) => (
                      <span
                        key={c}
                        className="h-5 w-5 rounded-full border border-white/20"
                        style={{ background: c }}
                        title={c}
                      />
                    ))}
                  </div>
                </div>
                <p className="mt-2 text-xs leading-relaxed text-white/50">{d.vibe}</p>
                <p className="mt-2 text-[10px] font-semibold uppercase tracking-wider text-white/40">
                  {d.fonts}
                </p>
              </button>
            );
          })}
        </div>

        <div className="lg:sticky lg:top-6 lg:self-start">
          <p className="mb-3 text-center text-[11px] font-semibold uppercase tracking-[0.22em] text-white/45">
            Preview · {meta.name}
          </p>
          <Preview />
          <button
            type="button"
            onClick={choose}
            className="mt-5 w-full rounded-xl bg-[#e11d2e] py-3.5 text-sm font-bold text-white transition hover:brightness-110"
          >
            {picked === active ? `Selected · ${meta.name} ✓` : `Use ${meta.name}`}
          </button>
          {picked && (
            <p className="mt-3 text-center text-xs text-white/55">
              Locked <span className="text-white">{DIRECTIONS.find((d) => d.id === picked)?.name}</span>.
              Tell the agent to implement that direction.
            </p>
          )}
          <a
            href="/"
            className="mt-4 block text-center text-xs text-white/40 underline-offset-2 hover:text-white/70 hover:underline"
            onClick={(e) => {
              e.preventDefault();
              const url = new URL(window.location.href);
              url.searchParams.delete("design");
              window.location.href = url.pathname + url.search;
            }}
          >
            Back to Coach K
          </a>
        </div>
      </div>
    </div>
  );
}

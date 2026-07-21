/**
 * Public marketing landing — Signal Strip (red + white).
 * Brand-first full-bleed hero, then Dayan's story, then unlock.
 */

import { useState } from "react";
import { CoachStorySections } from "./CoachStory";

const HERO = "/images/training-floor.jpg";
const SPEAKING = "/images/coach-dayan-speaking.jpg";
const PORTRAIT = "/images/coach-dayan.jpg";

export default function Landing({
  onUnlocked,
}: {
  onUnlocked: () => void;
}) {
  const [pw, setPw] = useState("");
  const [err, setErr] = useState("");

  function unlock() {
    const key = pw.trim();
    if (!key) {
      setErr("Enter your access password.");
      return;
    }
    localStorage.setItem("coachk_key", key);
    onUnlocked();
  }

  return (
    <div className="min-h-full overflow-y-auto bg-paper">
      {/* Hero — brand, one line, CTAs, full-bleed image */}
      <section className="relative min-h-[100dvh] overflow-hidden">
        <img
          src={HERO}
          alt=""
          className="ck-hero-pan absolute inset-0 h-full w-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-brand via-brand/75 to-ink/50" />
        <div className="absolute inset-0 bg-gradient-to-r from-brand/90 via-brand/40 to-transparent" />

        <div className="relative flex min-h-[100dvh] flex-col justify-end px-5 pb-[calc(2.5rem+env(safe-area-inset-bottom))] pt-24 sm:px-10 sm:pb-16">
          <p className="animate-rise font-display text-base font-extrabold tracking-[0.32em] text-white sm:text-lg">
            COACH K
          </p>
          <span className="animate-rise ck-signal mt-4 max-w-xs bg-white delay-75" />
          <h1 className="animate-rise mt-5 max-w-2xl font-display text-4xl font-black leading-[0.95] tracking-tight text-white delay-75 sm:text-6xl">
            No noise. Just the next signal.
          </h1>
          <p className="animate-rise mt-4 max-w-md text-base leading-relaxed text-white/90 delay-150 sm:text-lg">
            Dayan Kijege — personal strength coaching. One session. One cue.
          </p>
          <div className="animate-rise mt-8 flex flex-wrap gap-3 delay-200">
            <a
              href="#enter"
              className="ck-btn bg-white text-brand hover:bg-paper"
            >
              Enter Coach K
            </a>
            <a
              href="#story"
              className="ck-btn border-2 border-white text-white hover:bg-white/10"
            >
              My story
            </a>
          </div>
        </div>
      </section>

      {/* Portrait band */}
      <section className="relative overflow-hidden border-b border-line">
        <div className="mx-auto grid max-w-5xl items-center gap-8 px-5 py-12 sm:grid-cols-[minmax(0,220px)_1fr] sm:px-8 sm:py-16">
          <div className="relative mx-auto aspect-[3/4] w-48 overflow-hidden sm:mx-0 sm:w-full">
            <img
              src={SPEAKING}
              alt="Dayan Kijege — Coach K"
              className="h-full w-full object-cover object-top"
              onError={(e) => {
                const el = e.currentTarget;
                if (el.src.includes("speaking")) el.src = PORTRAIT;
                else el.src = "/images/hero-barbell.jpg";
              }}
            />
          </div>
          <div>
            <p className="ck-eyebrow">Coach</p>
            <span className="ck-signal-sm mt-3 max-w-[4rem]" />
            <h2 className="mt-3 font-display text-3xl font-black tracking-tight sm:text-4xl">
              Dayan Kijege
            </h2>
            <p className="mt-3 max-w-lg text-sm leading-relaxed text-mut sm:text-base">
              Athlete, basketball manager, Computer Science student, and the voice behind Coach K —
              personal strength coaching built for real schedules and ambitious goals.
            </p>
          </div>
        </div>
      </section>

      <CoachStorySections onCta={() => {
        document.getElementById("enter")?.scrollIntoView({ behavior: "smooth" });
      }} />

      {/* Unlock */}
      <section id="enter" className="relative overflow-hidden border-t border-line bg-brand">
        <div className="relative mx-auto max-w-md px-5 py-16 sm:px-8 sm:py-20">
          <p className="font-display text-[11px] font-bold uppercase tracking-[0.32em] text-white/80">
            Enter
          </p>
          <span className="mt-3 block h-0.5 w-16 bg-white" />
          <h2 className="mt-4 font-display text-3xl font-black tracking-tight text-white">
            Your training starts here.
          </h2>
          <p className="mt-3 text-sm leading-relaxed text-white/85">
            Private access for athletes training with Coach K. Enter your password to open Today,
            chat, plans, and progress.
          </p>
          <div className="mt-6">
            <input
              type="password"
              value={pw}
              onChange={(e) => {
                setPw(e.target.value);
                setErr("");
              }}
              onKeyDown={(e) => e.key === "Enter" && unlock()}
              placeholder="Password"
              className="ck-field border-white/30 bg-white text-ink"
              autoComplete="current-password"
            />
            {err && <p className="mt-2 text-xs text-white/90">{err}</p>}
            <button
              type="button"
              onClick={unlock}
              className="ck-btn mt-4 w-full bg-white text-brand hover:bg-paper"
            >
              Open Coach K
            </button>
          </div>
        </div>
      </section>

      <footer className="border-t border-line bg-paper px-5 py-8 text-center pb-[calc(2rem+env(safe-area-inset-bottom))]">
        <p className="ck-mark text-[11px]">COACH K</p>
        <p className="mt-2 text-[11px] text-mut">Dayan Kijege · Austin, TX</p>
      </footer>
    </div>
  );
}

/**
 * Public marketing landing — no API calls. Brand-first full-bleed hero,
 * then Dayan's story, then unlock to enter the app.
 */

import { useState } from "react";
import { CoachStorySections } from "./CoachStory";

const HERO = "/images/training-floor.jpg";
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
    <div className="min-h-full overflow-y-auto">
      {/* Hero — one composition: brand, headline, line, CTAs, full-bleed image */}
      <section className="relative min-h-[100dvh] overflow-hidden">
        <img
          src={HERO}
          alt=""
          className="ck-hero-pan absolute inset-0 h-full w-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-ink via-ink/80 to-ink/35" />
        <div className="absolute inset-0 bg-gradient-to-r from-ink/85 via-ink/40 to-transparent" />

        <div className="relative flex min-h-[100dvh] flex-col justify-end px-5 pb-[calc(2.5rem+env(safe-area-inset-bottom))] pt-24 sm:px-10 sm:pb-16">
          <p className="animate-rise ck-mark text-base sm:text-lg">COACH K</p>
          <h1 className="animate-rise mt-4 max-w-2xl font-display text-4xl font-black leading-[0.95] tracking-tight delay-75 sm:text-6xl">
            Train with a coach who shows up.
          </h1>
          <p className="animate-rise mt-4 max-w-md text-base leading-relaxed text-white/80 delay-150 sm:text-lg">
            Dayan Kijege — from the DRC to Austin. Science-grounded programming that adapts to you.
          </p>
          <div className="animate-rise mt-8 flex flex-wrap gap-3 delay-200">
            <a href="#enter" className="ck-btn ck-btn-primary">
              Enter Coach K
            </a>
            <a
              href="#story"
              className="ck-btn ck-btn-ghost border-white/25 text-white hover:border-white/50"
            >
              My story
            </a>
          </div>
        </div>
      </section>

      {/* Portrait band — brand continuity before story */}
      <section className="relative overflow-hidden border-b border-line/50">
        <div className="mx-auto grid max-w-5xl items-center gap-8 px-5 py-12 sm:grid-cols-[minmax(0,220px)_1fr] sm:px-8 sm:py-16">
          <div className="relative mx-auto aspect-[3/4] w-48 overflow-hidden rounded-2xl sm:mx-0 sm:w-full">
            <img
              src={PORTRAIT}
              alt="Dayan Kijege — Coach K"
              className="h-full w-full object-cover object-top"
              onError={(e) => {
                e.currentTarget.src = "/images/hero-barbell.jpg";
              }}
            />
          </div>
          <div>
            <p className="ck-eyebrow">Coach</p>
            <h2 className="mt-2 font-display text-3xl font-black tracking-tight sm:text-4xl">
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

      {/* Unlock — path into the app */}
      <section
        id="enter"
        className="relative overflow-hidden border-t border-line/60"
      >
        <img
          src="/images/hero-barbell.jpg"
          alt=""
          className="absolute inset-0 h-full w-full object-cover opacity-40"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-ink via-ink/90 to-ink/70" />
        <div className="relative mx-auto max-w-md px-5 py-16 sm:px-8 sm:py-20">
          <p className="ck-eyebrow">Enter</p>
          <h2 className="mt-3 font-display text-3xl font-black tracking-tight">
            Your training starts here.
          </h2>
          <p className="mt-3 text-sm leading-relaxed text-mut">
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
              className="ck-field"
              autoComplete="current-password"
            />
            {err && <p className="mt-2 text-xs text-amber-300">{err}</p>}
            <button
              type="button"
              onClick={unlock}
              className="ck-btn ck-btn-primary mt-4 w-full"
            >
              Open Coach K
            </button>
          </div>
        </div>
      </section>

      <footer className="border-t border-line/40 px-5 py-8 text-center pb-[calc(2rem+env(safe-area-inset-bottom))]">
        <p className="ck-mark text-[11px]">COACH K</p>
        <p className="mt-2 text-[11px] text-mut">Dayan Kijege · Austin, TX</p>
      </footer>
    </div>
  );
}

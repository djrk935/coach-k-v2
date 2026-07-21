/**
 * About Coach K — Dayan Kijege.
 * Drop the speaking photo at /public/images/coach-dayan.jpg to replace the hero.
 * Dayan can refine the bio copy anytime — this is a strong first draft.
 */

const COACH_PHOTO = "/images/coach-dayan.jpg";
const HERO_FALLBACK = "/images/hero-barbell.jpg";

export default function About({ onTalk }: { onTalk: () => void }) {
  return (
    <div className="flex-1 overflow-y-auto">
      {/* Full-bleed hero — brand first, one job */}
      <section className="relative min-h-[70vh] overflow-hidden sm:min-h-[78vh]">
        <img
          src={COACH_PHOTO}
          alt="Dayan Kijege — Coach K"
          className="absolute inset-0 h-full w-full object-cover object-top sm:object-[center_15%]"
          onError={(e) => {
            const el = e.currentTarget;
            if (el.src.endsWith("coach-dayan.jpg")) el.src = HERO_FALLBACK;
          }}
        />
        <div className="absolute inset-0 bg-gradient-to-t from-ink via-ink/75 to-ink/25" />
        <div className="absolute inset-0 bg-gradient-to-r from-ink/80 via-transparent to-transparent" />

        <div className="relative flex min-h-[70vh] flex-col justify-end px-5 pb-10 pt-24 sm:min-h-[78vh] sm:px-10 sm:pb-14">
          <p className="animate-rise font-display text-xs font-semibold tracking-[0.35em] text-brand">
            COACH K
          </p>
          <h1 className="animate-rise mt-3 max-w-xl font-display text-4xl font-black leading-[1.05] tracking-tight text-white delay-75 sm:text-6xl">
            Dayan Kijege
          </h1>
          <p className="animate-rise mt-4 max-w-md text-base leading-relaxed text-white/80 delay-150 sm:text-lg">
            Personal strength coach. Science in the program. Presence on the floor.
            Built for athletes who want honest feedback and real progress.
          </p>
          <div className="animate-rise mt-7 flex flex-wrap gap-3 delay-200">
            <button
              onClick={onTalk}
              className="rounded-xl bg-brand px-5 py-3 text-sm font-bold text-white transition hover:brightness-110 active:scale-[0.98]"
            >
              Talk to Coach K
            </button>
            <a
              href="#philosophy"
              className="rounded-xl border border-white/25 px-5 py-3 text-sm font-semibold text-white/90 transition hover:border-white/50"
            >
              How I coach
            </a>
          </div>
        </div>
      </section>

      {/* Philosophy — one section, one job */}
      <section id="philosophy" className="mx-auto max-w-3xl px-5 py-14 sm:px-8 sm:py-20">
        <p className="font-display text-xs font-semibold tracking-[0.3em] text-brand">PHILOSOPHY</p>
        <h2 className="mt-3 font-display text-3xl font-black tracking-tight sm:text-4xl">
          Train with intent. Recover with purpose.
        </h2>
        <p className="mt-5 text-base leading-relaxed text-mut sm:text-lg">
          Coach K isn’t a generic chatbot with workout tips. It’s Dayan’s coaching lens —
          periodized programming, readiness-aware load management, and book-grounded
          decisions — so every session moves you toward a clear goal instead of random
          hard work.
        </p>
      </section>

      {/* Atmosphere band */}
      <section className="relative overflow-hidden">
        <div className="grid sm:grid-cols-2">
          <div className="relative min-h-56 sm:min-h-72">
            <img
              src="/images/atmosphere-rack.jpg"
              alt=""
              className="absolute inset-0 h-full w-full object-cover"
            />
            <div className="absolute inset-0 bg-ink/40" />
          </div>
          <div className="relative flex flex-col justify-center bg-panel px-6 py-10 sm:px-10">
            <p className="font-display text-xs font-semibold tracking-[0.3em] text-brand">ON THE FLOOR</p>
            <h3 className="mt-3 font-display text-2xl font-black sm:text-3xl">
              From the whiteboard to the platform.
            </h3>
            <p className="mt-4 text-sm leading-relaxed text-mut sm:text-base">
              Dayan coaches with the same energy he brings to the mic — clear cues,
              high standards, and athletes who leave knowing exactly what to do next.
              Student assistant coach at St. Edward’s University. Leadership through
              Pure Ambition Sports. Always learning, always coaching.
            </p>
          </div>
        </div>
      </section>

      {/* What you get */}
      <section className="mx-auto max-w-3xl px-5 py-14 sm:px-8 sm:py-20">
        <p className="font-display text-xs font-semibold tracking-[0.3em] text-brand">WITH COACH K</p>
        <h2 className="mt-3 font-display text-3xl font-black tracking-tight sm:text-4xl">
          What working together looks like
        </h2>
        <ul className="mt-8 space-y-6">
          {[
            {
              title: "Living programs",
              body: "Not a PDF left to die in your notes. Today’s workout adapts to readiness, load, and what you actually logged.",
            },
            {
              title: "Honest assessment",
              body: "Physique photos, session logs, and check-ins get a coach’s eye — direct, specific, and actionable.",
            },
            {
              title: "Science without the fluff",
              body: "Grounded in a private textbook library with real citations. ACWR, RIR, and progression that make sense.",
            },
          ].map((item) => (
            <li key={item.title} className="border-l-2 border-brand/70 pl-4">
              <h3 className="font-display text-lg font-bold">{item.title}</h3>
              <p className="mt-1 text-sm leading-relaxed text-mut sm:text-base">{item.body}</p>
            </li>
          ))}
        </ul>
        <button
          onClick={onTalk}
          className="mt-10 rounded-xl bg-brand px-5 py-3 text-sm font-bold text-white transition hover:brightness-110 active:scale-[0.98]"
        >
          Start a conversation →
        </button>
        <p className="mt-8 text-xs text-mut/70">
          Bio draft for Dayan Kijege — send your story beats and we’ll lock the final voice.
        </p>
      </section>

      <div className="h-8 pb-[env(safe-area-inset-bottom)]" />
    </div>
  );
}

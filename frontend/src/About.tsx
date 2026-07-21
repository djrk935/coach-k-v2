/**
 * About Coach K — Dayan Kijege.
 * Public-facing story only. Photo: /public/images/coach-dayan.jpg
 * (Replace with the speaking photo anytime.)
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
          <p className="animate-rise ck-mark text-sm">COACH K</p>
          <h1 className="animate-rise mt-3 max-w-xl font-display text-4xl font-black leading-[1.05] tracking-tight text-white delay-75 sm:text-6xl">
            Dayan Kijege
          </h1>
          <p className="animate-rise mt-4 max-w-lg text-base leading-relaxed text-white/80 delay-150 sm:text-lg">
            From the Democratic Republic of Congo to Austin — athlete, coach, and builder.
            I train with purpose and coach the same way.
          </p>
          <div className="animate-rise mt-7 flex flex-wrap gap-3 delay-200">
            <button
              onClick={onTalk}
              className="rounded-xl bg-brand px-5 py-3 text-sm font-bold text-white transition hover:brightness-110 active:scale-[0.98]"
            >
              Talk to Coach K
            </button>
            <a
              href="#story"
              className="rounded-xl border border-white/25 px-5 py-3 text-sm font-semibold text-white/90 transition hover:border-white/50"
            >
              My story
            </a>
          </div>
        </div>
      </section>

      {/* Origin */}
      <section id="story" className="mx-auto max-w-3xl px-5 py-14 sm:px-8 sm:py-20">
        <p className="font-display text-xs font-semibold tracking-[0.3em] text-brand">THE STORY</p>
        <h2 className="mt-3 font-display text-3xl font-black tracking-tight sm:text-4xl">
          Built across languages, continents, and hard seasons.
        </h2>
        <p className="mt-5 text-base leading-relaxed text-mut sm:text-lg">
          I grew up in the DRC, graduated high school in 2020, and moved to the United States
          in 2021 to learn English and chase a bigger future. Today I’m a Computer Science junior
          at St. Edward’s University — and I still carry the discipline that got me here.
        </p>
        <p className="mt-4 text-base leading-relaxed text-mut sm:text-lg">
          I speak English, French, Lingala, Swahili, and Kinyamulenge. Faith is part of how I
          lead: with humility, consistency, and service. For years I’ve volunteered with The Well
          Austin Community Church — showing up twice a week, welcoming people, and helping build
          community that lasts.
        </p>
      </section>

      {/* Court */}
      <section className="relative overflow-hidden">
        <div className="grid sm:grid-cols-2">
          <div className="relative min-h-56 sm:min-h-80">
            <img
              src="/images/atmosphere-rack.jpg"
              alt=""
              className="absolute inset-0 h-full w-full object-cover"
            />
            <div className="absolute inset-0 bg-ink/45" />
          </div>
          <div className="relative flex flex-col justify-center bg-panel px-6 py-10 sm:px-10">
            <p className="font-display text-xs font-semibold tracking-[0.3em] text-brand">ON THE COURT</p>
            <h3 className="mt-3 font-display text-2xl font-black sm:text-3xl">
              6&apos;3&quot;. Basketball first. Athleticism always.
            </h3>
            <p className="mt-4 text-sm leading-relaxed text-mut sm:text-base">
              Basketball is one of my deepest passions — dunking consistently, building real
              explosiveness, and chasing a physique that’s athletic and sharp. I’m a student
              manager for the St. Edward’s Women’s Basketball team: film, breakdown, bench support,
              and learning the game from the coaching side every day.
            </p>
            <p className="mt-3 text-sm leading-relaxed text-mut sm:text-base">
              That dual view — athlete and staff — is why Coach K doesn’t guess. We program for
              the body you have today and the athlete you’re becoming.
            </p>
          </div>
        </div>
      </section>

      {/* Philosophy */}
      <section id="philosophy" className="mx-auto max-w-3xl px-5 py-14 sm:px-8 sm:py-20">
        <p className="font-display text-xs font-semibold tracking-[0.3em] text-brand">PHILOSOPHY</p>
        <h2 className="mt-3 font-display text-3xl font-black tracking-tight sm:text-4xl">
          Ambitious goals. Measurable work. No fluff.
        </h2>
        <p className="mt-5 text-base leading-relaxed text-mut sm:text-lg">
          I don’t just want answers — I want plans you can execute. The same way I approach
          school, internships, and systems work: clear documentation, real skills, and progress
          you can feel. Coach K brings that lens to training — periodized programs, readiness-aware
          load, honest physique feedback, and science grounded in a private coaching library.
        </p>
        <p className="mt-4 text-base leading-relaxed text-mut sm:text-lg">
          Long-term, I’m building a life that lets me help my family and lead with excellence —
          in technology and on the floor. Training is part of that foundation.
        </p>
      </section>

      {/* What you get */}
      <section className="border-t border-line/60 bg-panel/40">
        <div className="mx-auto max-w-3xl px-5 py-14 sm:px-8 sm:py-20">
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
                title: "Athlete-to-athlete honesty",
                body: "I’ve trained through setbacks and rebuilds. Feedback is direct, specific, and built for real progress — dunks, strength, conditioning, or recomposition.",
              },
              {
                title: "Science without the fluff",
                body: "Book-grounded programming with real citations. ACWR, RIR, and progression that make sense for your schedule and goals.",
              },
              {
                title: "A coach who shows up",
                body: "Same standard I bring to film sessions, volunteering, and enterprise IT work: prepare well, communicate clearly, and keep raising the bar.",
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
            Start training with Coach K →
          </button>
        </div>
      </section>

      <div className="h-8 pb-[env(safe-area-inset-bottom)]" />
    </div>
  );
}

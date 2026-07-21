/**
 * Shared Coach K story sections — used by public Landing and in-app About.
 */

export function CoachStorySections({ onCta }: { onCta: () => void }) {
  return (
    <>
      <section id="story" className="mx-auto max-w-3xl px-5 py-14 sm:px-8 sm:py-20">
        <p className="ck-eyebrow">The story</p>
        <span className="ck-signal-sm mt-3 max-w-[3rem]" />
        <h2 className="mt-3 font-display text-3xl font-black tracking-tight sm:text-4xl">
          Built across languages, continents, and hard seasons.
        </h2>
        <p className="mt-5 text-base leading-relaxed text-mut sm:text-lg">
          I grew up in the DRC, graduated high school in 2020, and moved to the United States
          in 2021 to learn English and chase a bigger future. Today I&apos;m a Computer Science junior
          at St. Edward&apos;s University — and I still carry the discipline that got me here.
        </p>
        <p className="mt-4 text-base leading-relaxed text-mut sm:text-lg">
          I speak English, French, Lingala, Swahili, and Kinyamulenge. Faith is part of how I
          lead: with humility, consistency, and service. For years I&apos;ve volunteered with The Well
          Austin Community Church — showing up twice a week, welcoming people, and helping build
          community that lasts.
        </p>
      </section>

      <section className="relative overflow-hidden">
        <div className="grid sm:grid-cols-2">
          <div className="relative min-h-56 sm:min-h-80">
            <img
              src="/images/atmosphere-rack.jpg"
              alt=""
              className="absolute inset-0 h-full w-full object-cover"
            />
            <div className="absolute inset-0 bg-brand/55" />
          </div>
          <div className="relative flex flex-col justify-center bg-paper px-6 py-10 sm:px-10">
            <p className="ck-eyebrow">On the court</p>
            <span className="ck-signal-sm mt-3 max-w-[3rem]" />
            <h3 className="mt-3 font-display text-2xl font-black sm:text-3xl">
              6&apos;3&quot;. Basketball first. Athleticism always.
            </h3>
            <p className="mt-4 text-sm leading-relaxed text-mut sm:text-base">
              Basketball is one of my deepest passions — dunking consistently, building real
              explosiveness, and chasing a physique that&apos;s athletic and sharp. I&apos;m a student
              manager for the St. Edward&apos;s Women&apos;s Basketball team: film, breakdown, bench support,
              and learning the game from the coaching side every day.
            </p>
            <p className="mt-3 text-sm leading-relaxed text-mut sm:text-base">
              That dual view — athlete and staff — is why Coach K doesn&apos;t guess. We program for
              the body you have today and the athlete you&apos;re becoming.
            </p>
          </div>
        </div>
      </section>

      <section id="philosophy" className="mx-auto max-w-3xl px-5 py-14 sm:px-8 sm:py-20">
        <p className="ck-eyebrow">Philosophy</p>
        <span className="ck-signal-sm mt-3 max-w-[3rem]" />
        <h2 className="mt-3 font-display text-3xl font-black tracking-tight sm:text-4xl">
          Ambitious goals. Measurable work. No fluff.
        </h2>
        <p className="mt-5 text-base leading-relaxed text-mut sm:text-lg">
          I don&apos;t just want answers — I want plans you can execute. The same way I approach
          school, internships, and systems work: clear documentation, real skills, and progress
          you can feel. Coach K brings that lens to training — periodized programs, readiness-aware
          load, honest physique feedback, and science grounded in a private coaching library.
        </p>
        <p className="mt-4 text-base leading-relaxed text-mut sm:text-lg">
          Long-term, I&apos;m building a life that lets me help my family and lead with excellence —
          in technology and on the floor. Training is part of that foundation.
        </p>
      </section>

      <section className="border-t border-line bg-paper">
        <div className="mx-auto max-w-3xl px-5 py-14 sm:px-8 sm:py-20">
          <p className="ck-eyebrow">With Coach K</p>
          <span className="ck-signal-sm mt-3 max-w-[3rem]" />
          <h2 className="mt-3 font-display text-3xl font-black tracking-tight sm:text-4xl">
            What working together looks like
          </h2>
          <ul className="mt-8 space-y-6">
            {[
              {
                title: "Living programs",
                body: "Not a PDF left to die in your notes. Today's workout adapts to readiness, load, and what you actually logged.",
              },
              {
                title: "Athlete-to-athlete honesty",
                body: "I've trained through setbacks and rebuilds. Feedback is direct, specific, and built for real progress — dunks, strength, conditioning, or recomposition.",
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
              <li key={item.title} className="border-l-[3px] border-brand pl-4">
                <h3 className="font-display text-lg font-bold">{item.title}</h3>
                <p className="mt-1 text-sm leading-relaxed text-mut sm:text-base">{item.body}</p>
              </li>
            ))}
          </ul>
          <button
            type="button"
            onClick={onCta}
            className="ck-btn ck-btn-primary mt-10"
          >
            Start training with Coach K →
          </button>
        </div>
      </section>
    </>
  );
}

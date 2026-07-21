/**
 * About Coach K — Dayan Kijege.
 * In-app story (same narrative as the public landing).
 *
 * Photo: prefers /images/coach-dayan-speaking.jpg when present,
 * else /images/coach-dayan.jpg. Drop your speaking headshot as
 * coach-dayan-speaking.jpg anytime to upgrade the hero.
 */

import { CoachStorySections } from "./CoachStory";

const SPEAKING_PHOTO = "/images/coach-dayan-speaking.jpg";
const COACH_PHOTO = "/images/coach-dayan.jpg";
const HERO_FALLBACK = "/images/hero-barbell.jpg";

export default function About({ onTalk }: { onTalk: () => void }) {
  return (
    <div className="flex-1 overflow-y-auto bg-paper">
      <section className="relative min-h-[70vh] overflow-hidden sm:min-h-[78vh]">
        <img
          src={SPEAKING_PHOTO}
          alt="Dayan Kijege — Coach K"
          className="absolute inset-0 h-full w-full object-cover object-top sm:object-[center_18%]"
          onError={(e) => {
            const el = e.currentTarget;
            if (el.src.includes("speaking")) el.src = COACH_PHOTO;
            else if (el.src.includes("coach-dayan")) el.src = HERO_FALLBACK;
          }}
        />
        <div className="absolute inset-0 bg-gradient-to-t from-brand via-brand/70 to-ink/40" />
        <div className="absolute inset-0 bg-gradient-to-r from-brand/85 via-transparent to-transparent" />

        <div className="relative flex min-h-[70vh] flex-col justify-end px-5 pb-10 pt-24 sm:min-h-[78vh] sm:px-10 sm:pb-14">
          <p className="animate-rise font-display text-sm font-extrabold tracking-[0.32em] text-white">
            COACH K
          </p>
          <span className="animate-rise mt-3 block h-0.5 w-20 bg-white delay-75" />
          <h1 className="animate-rise mt-4 max-w-xl font-display text-4xl font-black leading-[1.05] tracking-tight text-white delay-75 sm:text-6xl">
            Dayan Kijege
          </h1>
          <p className="animate-rise mt-4 max-w-lg text-base leading-relaxed text-white/90 delay-150 sm:text-lg">
            From the Democratic Republic of Congo to Austin — athlete, coach, and builder.
            I train with purpose and coach the same way.
          </p>
          <div className="animate-rise mt-7 flex flex-wrap gap-3 delay-200">
            <button
              type="button"
              onClick={onTalk}
              className="ck-btn bg-white text-brand hover:bg-paper"
            >
              Talk to Coach K
            </button>
            <a
              href="#story"
              className="ck-btn border-2 border-white text-white hover:bg-white/10"
            >
              My story
            </a>
          </div>
        </div>
      </section>

      <CoachStorySections onCta={onTalk} />

      <div className="h-8 pb-[env(safe-area-inset-bottom)]" />
    </div>
  );
}

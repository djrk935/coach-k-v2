import { useEffect, useRef, useState } from "react";
import { api, ChatMeta, Dashboard, fileToDataUrl, keyed, Msg } from "./api";
import About from "./About";
import Calendar from "./Calendar";
import Landing from "./Landing";
import OfflineBanner from "./OfflineBanner";
import Onboarding from "./Onboarding";
import Progress from "./Progress";
import Settings from "./Settings";
import Templates from "./Templates";
import Today from "./Today";

// Minimal markdown: **bold** + [links](url); /api links get the auth key.
function md(text: string) {
  const html = text
    .replace(/&/g, "&amp;").replace(/</g, "&lt;")
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(
      /\[(.+?)\]\((.+?)\)/g,
      '<a href="$2" target="_blank" class="text-brand underline">$1</a>',
    )
    .replace(/href="(\/api\/[^"]+)"/g, (_m, p: string) => `href="${keyed(p)}"`)
    .replace(/\n/g, "<br/>");
  return { __html: html };
}

function LockScreen({
  onUnlock,
  onBack,
}: {
  onUnlock: () => void;
  onBack?: () => void;
}) {
  const [pw, setPw] = useState("");
  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center sm:items-center">
      <img
        src="/images/hero-barbell.jpg"
        alt=""
        className="absolute inset-0 h-full w-full object-cover"
      />
      <div className="absolute inset-0 bg-gradient-to-t from-brand via-brand/80 to-ink/45" />
      <div className="absolute inset-0 bg-gradient-to-r from-brand/85 via-transparent to-transparent" />
      <div className="relative w-full max-w-md px-5 pb-[calc(2rem+env(safe-area-inset-bottom))] pt-16 sm:px-6 sm:pb-10">
        <p className="animate-rise font-display text-sm font-extrabold tracking-[0.32em] text-white">
          COACH K
        </p>
        <span className="animate-rise mt-3 block h-0.5 w-20 bg-white delay-75" />
        <h1 className="animate-rise mt-4 font-display text-4xl font-black leading-[0.95] tracking-tight text-white delay-75 sm:text-5xl">
          No noise. Just the next signal.
        </h1>
        <p className="animate-rise mt-4 max-w-sm text-[15px] leading-relaxed text-white/90 delay-150">
          Dayan Kijege — science-grounded programming. Honest feedback. Workouts that adapt to you.
        </p>
        <div className="animate-rise mt-8 border border-white/30 bg-white p-5 delay-200">
          <p className="mb-3 text-[11px] font-semibold uppercase tracking-[0.2em] text-brand">
            Enter to continue
          </p>
          <input
            type="password"
            value={pw}
            onChange={(e) => setPw(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && pw) {
                localStorage.setItem("coachk_key", pw);
                onUnlock();
              }
            }}
            placeholder="Password"
            autoFocus
            className="ck-field"
          />
          {onBack && (
            <button
              type="button"
              onClick={onBack}
              className="mt-3 w-full py-2 text-xs font-semibold text-mut hover:text-brand"
            >
              ← Back to landing
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

type FormMedia = { matched: string; image_urls: string[]; instructions: string[] };

function FormLookup() {
  const [q, setQ] = useState("");
  const [media, setMedia] = useState<FormMedia | null>(null);
  const [err, setErr] = useState("");
  const [frame, setFrame] = useState(0);

  useEffect(() => {
    if (!media) return;
    const t = setInterval(() => setFrame((f) => 1 - f), 900);
    return () => clearInterval(t);
  }, [media]);

  async function lookup() {
    if (!q.trim()) return;
    setErr("");
    setMedia(null);
    const r = await api(`/api/exercises/${encodeURIComponent(q.trim())}/media`);
    if (r.ok) setMedia(await r.json());
    else setErr("No form match — try a standard name like “Back Squat”.");
  }

  return (
    <section className="border-b border-line py-4">
      <h3 className="mb-2 font-display text-[11px] font-semibold uppercase tracking-[0.2em] text-mut">Form Check</h3>
      <div className="flex gap-2">
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && lookup()}
          placeholder="e.g. Romanian Deadlift"
          className="ck-field min-w-0 flex-1 py-2 text-sm"
        />
        <button onClick={lookup} className="ck-btn ck-btn-primary px-3 py-2 text-xs">
          Go
        </button>
      </div>
      {err && <p className="mt-2 text-xs text-mut">{err}</p>}
      {media && (
        <div className="mt-3">
          <img
            src={media.image_urls[frame] ?? media.image_urls[0]}
            alt={media.matched}
            className="w-full rounded-lg border border-line bg-white"
          />
          <p className="mt-1.5 text-xs font-semibold">{media.matched}</p>
          {media.instructions[0] && (
            <p className="mt-1 text-xs leading-relaxed text-mut">
              {media.instructions.slice(0, 2).join(" ")}
            </p>
          )}
        </div>
      )}
    </section>
  );
}

function acwrTone(acwr: number | null) {
  if (acwr == null) return { label: "building baseline", cls: "text-mut" };
  if (acwr > 1.5) return { label: "spike — back off", cls: "text-brand" };
  if (acwr > 1.3) return { label: "elevated", cls: "text-amber-400" };
  if (acwr < 0.8) return { label: "detraining", cls: "text-sky-700" };
  return { label: "in the zone", cls: "text-emerald-700" };
}

/** Shared dashboard panels — desktop sidebar + phone drawer. */
function DashPanels({ dash }: { dash: Dashboard | null }) {
  const today = dash?.readiness?.[0];
  const acwr = dash?.load?.acwr ?? null;
  const tone = acwrTone(acwr);
  const profile = dash?.profile ?? {};
  const oneRms = ((profile as Record<string, unknown>).lifts_1rm ??
    (profile as Record<string, unknown>).one_rms ??
    {}) as Record<string, number>;

  return (
    <>
      <section className="border-b border-line py-4">
        <h3 className="mb-2 font-display text-[11px] font-semibold uppercase tracking-[0.2em] text-mut">Training Load</h3>
        <div className="font-display text-3xl font-black">
          {acwr ?? "—"} <span className={`text-sm font-semibold ${tone.cls}`}>{tone.label}</span>
        </div>
        <p className="mt-1 text-xs text-mut">ACWR · {dash?.load?.sessions_28d ?? 0} sessions / 28d</p>
      </section>

      <section className="border-b border-line py-4">
        <h3 className="mb-2 font-display text-[11px] font-semibold uppercase tracking-[0.2em] text-mut">
          Today's Readiness
        </h3>
        {today ? (
          <ul className="space-y-1 text-sm">
            {Object.entries(today)
              .filter(([k]) => k !== "date" && k !== "notes")
              .map(([k, v]) => (
                <li key={k} className="flex justify-between">
                  <span className="text-mut">{k.replace(/_/g, " ")}</span>
                  <span className="font-semibold">{String(v)}</span>
                </li>
              ))}
          </ul>
        ) : (
          <p className="text-sm text-mut">Tell Coach K how you slept.</p>
        )}
      </section>

      {Object.keys(oneRms).length > 0 && (
        <section className="border-b border-line py-4">
          <h3 className="mb-2 font-display text-[11px] font-semibold uppercase tracking-[0.2em] text-mut">1RMs</h3>
          <ul className="space-y-1 text-sm">
            {Object.entries(oneRms).map(([lift, lbs]) => (
              <li key={lift} className="flex justify-between">
                <span className="text-mut">{lift}</span>
                <span className="font-semibold">{lbs} lbs</span>
              </li>
            ))}
          </ul>
        </section>
      )}

      <FormLookup />

      <section className="border-b border-line py-4">
        <h3 className="mb-2 font-display text-[11px] font-semibold uppercase tracking-[0.2em] text-mut">Programs</h3>
        {dash?.programs?.length ? (
          <ul className="divide-y divide-line">
            {dash.programs.map((p) => (
              <li key={p.id}>
                <a
                  href={keyed(`/api/programs/${p.id}/pdf`)}
                  target="_blank"
                  className="block py-2.5 text-sm hover:text-brand"
                >
                  <span className="font-semibold">{p.name}</span>
                  <span className="mt-0.5 block text-xs text-mut">
                    {p.goal ?? "general"} · {p.created_at.slice(0, 10)} · PDF ↗
                  </span>
                </a>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-mut">No programs yet — ask for one.</p>
        )}
      </section>
    </>
  );
}

export default function App() {
  const [msgs, setMsgs] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [dash, setDash] = useState<Dashboard | null>(null);
  const [booting, setBooting] = useState(true);
  const [showLanding, setShowLanding] = useState(false);
  const [locked, setLocked] = useState(false);
  const [chats, setChats] = useState<ChatMeta[]>([]);
  const [chatId, setChatId] = useState<string | null>(null);
  const [view, setView] = useState<"today" | "chat" | "templates" | "progress" | "calendar" | "about">("today");
  const [showSettings, setShowSettings] = useState(false);
  const [showDash, setShowDash] = useState(false);
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [images, setImages] = useState<string[]>([]);
  const bottomRef = useRef<HTMLDivElement>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  const refreshDash = () =>
    api("/api/dashboard")
      .then((r) => {
        if (r.status === 401) {
          if (!localStorage.getItem("coachk_key")) setShowLanding(true);
          else setLocked(true);
          return;
        }
        setLocked(false);
        setShowLanding(false);
        return r.json().then((d: Dashboard) => {
          setDash(d);
          const profile = (d.profile || {}) as Record<string, unknown>;
          const localDone = localStorage.getItem("coachk_onboarded") === "1";
          if (!profile.onboarded && !localDone) setShowOnboarding(true);
        });
      })
      .catch(() => {});

  const loadChats = async () => {
    const r = await api("/api/chats");
    if (!r.ok) return;
    const list: ChatMeta[] = await r.json();
    setChats(list);
    if (!chatId && list[0]) selectChat(list[0].id);
  };

  async function selectChat(id: string) {
    setChatId(id);
    setView("chat");
    const r = await api(`/api/chats/${id}/messages`);
    setMsgs(r.ok ? await r.json() : []);
  }

  async function newChat() {
    const r = await api("/api/chats", { method: "POST" });
    if (!r.ok) return;
    const { id } = await r.json();
    setChats((c) => [{ id, title: "New chat", created_at: "" }, ...c]);
    setChatId(id);
    setMsgs([]);
    setView("chat");
  }

  function enterApp() {
    setShowLanding(false);
    setLocked(false);
    setBooting(false);
    refreshDash();
    loadChats();
  }

  useEffect(() => {
    // Probe without flashing the app shell: open access → app; 401 + no key → landing.
    api("/api/dashboard")
      .then(async (r) => {
        if (r.ok) {
          const d: Dashboard = await r.json();
          setDash(d);
          setShowLanding(false);
          setLocked(false);
          const profile = (d.profile || {}) as Record<string, unknown>;
          const localDone = localStorage.getItem("coachk_onboarded") === "1";
          if (!profile.onboarded && !localDone) setShowOnboarding(true);
          loadChats();
        } else if (r.status === 401) {
          if (localStorage.getItem("coachk_key")) setLocked(true);
          else setShowLanding(true);
        } else if (!localStorage.getItem("coachk_key")) {
          setShowLanding(true);
        }
      })
      .catch(() => {
        if (!localStorage.getItem("coachk_key")) setShowLanding(true);
      })
      .finally(() => setBooting(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [msgs]);

  async function attach(files: FileList | null) {
    if (!files) return;
    const urls: string[] = [];
    for (const f of Array.from(files).slice(0, 4 - images.length)) {
      urls.push(await fileToDataUrl(f));
    }
    setImages((im) => [...im, ...urls]);
  }

  async function send() {
    const message = input.trim();
    if ((!message && !images.length) || busy) return;
    const sent = images;
    setInput("");
    setImages([]);
    setBusy(true);
    const shown = sent.length
      ? `📷 ${sent.length} photo${sent.length > 1 ? "s" : ""} — ${message}`.trim()
      : message;
    setMsgs((m) => [...m, { role: "user", text: shown }, { role: "assistant", text: "" }]);

    try {
      const res = await api("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, chat_id: chatId, images: sent }),
      });
      if (res.status === 401) {
        setLocked(true);
        setMsgs((m) => m.slice(0, -2));
        return;
      }
      const reader = res.body!.getReader();
      const dec = new TextDecoder();
      let buf = "";
      for (;;) {
        const { done, value } = await reader.read();
        if (done) break;
        buf += dec.decode(value, { stream: true });
        const lines = buf.split("\n\n");
        buf = lines.pop()!;
        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          const ev = JSON.parse(line.slice(6));
          if (ev.type === "token" || ev.type === "error") {
            const add = ev.type === "error" ? `⚠ ${ev.text}` : ev.text;
            setMsgs((m) => {
              const copy = [...m];
              copy[copy.length - 1] = {
                role: "assistant",
                text: copy[copy.length - 1].text + add,
              };
              return copy;
            });
          }
          if (ev.type === "done" && ev.chat_id) {
            if (!chatId) setChatId(ev.chat_id);
            api("/api/chats").then((r) => {
              if (r.ok) r.json().then(setChats);
            });
          }
        }
      }
    } catch {
      setMsgs((m) => [...m.slice(0, -1), { role: "assistant", text: "⚠ backend unreachable" }]);
    } finally {
      setBusy(false);
      refreshDash();
    }
  }

  if (booting) {
    return <div className="h-full bg-paper" />;
  }

  if (showLanding) {
    return <Landing onUnlocked={enterApp} />;
  }

  if (locked) {
    return (
      <LockScreen
        onUnlock={enterApp}
        onBack={() => {
          localStorage.removeItem("coachk_key");
          setLocked(false);
          setShowLanding(true);
        }}
      />
    );
  }

  if (showOnboarding) {
    return (
      <Onboarding
        onComplete={() => {
          setShowOnboarding(false);
          setView("today");
          refreshDash();
        }}
      />
    );
  }

  const profile = (dash?.profile ?? {}) as Record<string, unknown>;

  return (
    <div className="flex h-full min-h-0 flex-col">
      <OfflineBanner />
      <div className="flex min-h-0 flex-1">
      {/* ===== Main column ===== */}
      <main className="flex min-w-0 flex-1 flex-col">
        <header className="flex flex-wrap items-center gap-2 border-b border-line/70 bg-paper/95 px-3 py-2.5 pt-[calc(0.55rem+env(safe-area-inset-top))] backdrop-blur-xl sm:gap-3 sm:px-5 sm:py-3">
          <button
            onClick={() => setView("about")}
            className="ck-mark text-[13px] transition hover:brightness-110 sm:text-sm"
            title="About Coach K"
          >
            COACH K
          </button>
          {/* Desktop: chat tools sit next to the brand. Phones: full-width second row. */}
          {view === "chat" && (
            <div className="order-last flex w-full items-center gap-2 sm:order-none sm:w-auto">
              <select
                value={chatId ?? ""}
                onChange={(e) => selectChat(e.target.value)}
                className="min-w-0 flex-1 rounded-lg border border-line bg-panel px-2 py-1.5 text-xs outline-none sm:max-w-44 sm:flex-none"
              >
                {chats.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.title}
                  </option>
                ))}
              </select>
              <button
                onClick={newChat}
                className="shrink-0 rounded-lg border border-line px-2.5 py-1.5 text-xs font-semibold hover:border-brand"
              >
                + New
              </button>
            </div>
          )}
          <div className="flex-1" />
          <nav className="flex flex-wrap items-end gap-0.5 sm:gap-1">
            {([
              ["today", "today"],
              ["chat", "chat"],
              ["templates", "plans"],
              ["progress", "stats"],
              ["calendar", "week"],
              ["about", "about"],
            ] as const).map(([v, label]) => (
              <button
                key={v}
                onClick={() => setView(v)}
                data-active={view === v}
                className="ck-nav-tab sm:text-[0.7rem]"
              >
                {label}
              </button>
            ))}
          </nav>
          {/* Phone/tablet: open the dashboard drawer (desktop uses the sidebar). */}
          <button
            onClick={() => setShowDash(true)}
            className="border border-fg px-2.5 py-1.5 text-[10px] font-bold uppercase tracking-wider hover:border-brand hover:text-brand lg:hidden"
            title="Stats & tools"
          >
            Stats
          </button>
          <button
            onClick={() => setShowSettings(true)}
            className="border border-fg px-2.5 py-1.5 text-[10px] font-bold uppercase tracking-wider hover:border-brand hover:text-brand"
            title="Settings"
          >
            Settings
          </button>
        </header>

        {view === "today" ? (
          <Today onGoToTemplates={() => setView("templates")} />
        ) : view === "templates" ? (
          <Templates
            onPersonalize={(name) => {
              setView("chat");
              setInput(
                `Personalize the "${name}" template for me — adapt it to my profile, 1RMs, and readiness, then generate the program.`,
              );
            }}
            onActivated={() => {
              setView("today");
              refreshDash();
            }}
          />
        ) : view === "progress" ? (
          <Progress />
        ) : view === "calendar" ? (
          <Calendar onOpenToday={() => setView("today")} />
        ) : view === "about" ? (
          <About
            onTalk={() => {
              setView("chat");
              if (!input) setInput("Hey Coach — here's what I'm training for: ");
            }}
          />
        ) : (
          <>
            <div className="mx-auto w-full max-w-3xl flex-1 space-y-4 overflow-y-auto px-4 py-5 sm:px-6 sm:py-6">
              {msgs.length === 0 && (
                <div className="animate-fade relative mx-auto mt-6 overflow-hidden sm:mt-10">
                  <img
                    src="/images/atmosphere-kettle.jpg"
                    alt=""
                    className="absolute inset-0 h-full w-full object-cover"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-brand via-brand/70 to-ink/50" />
                  <div className="relative px-6 py-14 text-left sm:py-20">
                    <p className="font-display text-xs font-extrabold tracking-[0.32em] text-white">
                      COACH K
                    </p>
                    <span className="mt-3 block h-0.5 w-16 bg-white" />
                    <p className="mt-4 font-display text-2xl font-black tracking-tight text-white sm:text-3xl">
                      What are we training for?
                    </p>
                    <p className="mt-3 max-w-md text-sm leading-relaxed text-white/90">
                      Ask for a program, log a session, check in — or attach physique photos for an honest assessment.
                    </p>
                  </div>
                </div>
              )}
              {msgs.map((m, i) => (
                <div key={i} className={m.role === "user" ? "flex justify-end" : "flex"}>
                  <div
                    className={
                      m.role === "user"
                        ? "max-w-[88%] bg-brand px-4 py-2.5 text-white sm:max-w-[70%]"
                        : "max-w-[92%] border border-line bg-panel px-4 py-2.5 sm:max-w-[85%]"
                    }
                    dangerouslySetInnerHTML={md(m.text || (busy && i === msgs.length - 1 ? "…" : ""))}
                  />
                </div>
              ))}
              <div ref={bottomRef} />
            </div>

            <footer className="border-t border-line bg-paper p-3 pb-[calc(0.75rem+env(safe-area-inset-bottom))] sm:p-4">
              <div className="mx-auto w-full max-w-3xl">
                {images.length > 0 && (
                  <div className="mb-2 flex gap-2 overflow-x-auto">
                    {images.map((u, i) => (
                      <div key={i} className="relative shrink-0">
                        <img src={u} alt="" className="h-14 w-14 rounded-lg object-cover" />
                        <button
                          onClick={() => setImages(images.filter((_, j) => j !== i))}
                          className="absolute -right-1.5 -top-1.5 flex h-5 w-5 items-center justify-center rounded-full bg-brand text-xs text-white"
                        >
                          ✕
                        </button>
                      </div>
                    ))}
                  </div>
                )}
                <div className="flex gap-2">
                  <input
                    ref={fileRef}
                    type="file"
                    accept="image/*"
                    multiple
                    hidden
                    onChange={(e) => {
                      attach(e.target.files);
                      e.target.value = "";
                    }}
                  />
                  <button
                    onClick={() => fileRef.current?.click()}
                    title="Attach physique photos"
                    className="ck-btn ck-btn-ghost shrink-0 px-3 text-xs"
                  >
                    Photo
                  </button>
                  <input
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && send()}
                    placeholder="Ask Coach K…"
                    className="ck-field min-w-0 flex-1 py-3 sm:px-4"
                  />
                  <button
                    onClick={send}
                    disabled={busy}
                    className="ck-btn ck-btn-primary shrink-0 disabled:opacity-40"
                  >
                    Send
                  </button>
                </div>
              </div>
            </footer>
          </>
        )}
      </main>

      {/* ===== Desktop sidebar (MacBook / wide screens) ===== */}
      <aside className="hidden w-80 shrink-0 flex-col gap-4 overflow-y-auto border-l border-line p-5 lg:flex">
        <DashPanels dash={dash} />
      </aside>
      </div>

      {/* ===== Phone/tablet stats drawer ===== */}
      {showDash && (
        <div
          className="fixed inset-0 z-40 flex justify-end bg-ink/40 lg:hidden"
          onClick={() => setShowDash(false)}
        >
          <div
            className="flex h-full w-full max-w-sm flex-col border-l border-line bg-paper pt-[env(safe-area-inset-top)]"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between border-b border-line px-4 py-3">
              <h2 className="text-sm font-black tracking-[0.2em] text-brand">STATS</h2>
              <button
                onClick={() => setShowDash(false)}
                className="rounded-lg border border-line px-2.5 py-1.5 text-xs font-semibold hover:border-brand"
              >
                ✕
              </button>
            </div>
            <div className="flex flex-1 flex-col gap-4 overflow-y-auto p-4 pb-[calc(1rem+env(safe-area-inset-bottom))]">
              <DashPanels dash={dash} />
            </div>
          </div>
        </div>
      )}

      {showSettings && (
        <Settings
          profile={profile}
          onClose={() => setShowSettings(false)}
          onSaved={refreshDash}
        />
      )}
    </div>
  );
}

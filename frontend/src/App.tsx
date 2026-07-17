import { useEffect, useRef, useState } from "react";
import { api, appKey, ChatMeta, Dashboard, fileToDataUrl, keyed, Msg } from "./api";
import Settings from "./Settings";
import Templates from "./Templates";

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

function LockScreen({ onUnlock }: { onUnlock: () => void }) {
  const [pw, setPw] = useState("");
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-ink/95">
      <div className="w-80 rounded-2xl bg-panel p-6">
        <div className="mb-1 font-black tracking-[0.3em] text-brand">COACH K</div>
        <p className="mb-4 text-sm text-mut">Enter the app password to continue.</p>
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
          className="w-full rounded-lg border border-line bg-ink px-3 py-2 outline-none focus:border-brand"
        />
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
    <section className="rounded-xl bg-panel p-4">
      <h3 className="mb-2 text-xs font-semibold uppercase tracking-wider text-mut">Form Check</h3>
      <div className="flex gap-2">
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && lookup()}
          placeholder="e.g. Romanian Deadlift"
          className="w-full min-w-0 flex-1 rounded-lg border border-line bg-ink px-3 py-2 text-sm outline-none placeholder:text-mut focus:border-brand"
        />
        <button onClick={lookup} className="rounded-lg bg-brand px-3 text-sm font-semibold text-white">
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
  if (acwr < 0.8) return { label: "detraining", cls: "text-sky-400" };
  return { label: "in the zone", cls: "text-emerald-400" };
}

export default function App() {
  const [msgs, setMsgs] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [dash, setDash] = useState<Dashboard | null>(null);
  const [locked, setLocked] = useState(false);
  const [chats, setChats] = useState<ChatMeta[]>([]);
  const [chatId, setChatId] = useState<string | null>(null);
  const [view, setView] = useState<"chat" | "templates">("chat");
  const [showSettings, setShowSettings] = useState(false);
  const [images, setImages] = useState<string[]>([]);
  const bottomRef = useRef<HTMLDivElement>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  const refreshDash = () =>
    api("/api/dashboard")
      .then((r) => {
        if (r.status === 401) setLocked(true);
        else return r.json().then(setDash);
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

  useEffect(() => {
    refreshDash();
    loadChats();
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

  if (locked) {
    return (
      <LockScreen
        onUnlock={() => {
          setLocked(false);
          refreshDash();
          loadChats();
        }}
      />
    );
  }

  const today = dash?.readiness?.[0];
  const acwr = dash?.load?.acwr ?? null;
  const tone = acwrTone(acwr);
  const profile = dash?.profile ?? {};
  const oneRms = ((profile as Record<string, unknown>).lifts_1rm ??
    (profile as Record<string, unknown>).one_rms ??
    {}) as Record<string, number>;

  return (
    <div className="flex h-full">
      {/* ===== Main column ===== */}
      <main className="flex flex-1 flex-col">
        <header className="flex items-center gap-3 border-b border-line px-4 py-3">
          <span className="font-black tracking-[0.3em] text-brand">COACH K</span>
          <select
            value={chatId ?? ""}
            onChange={(e) => selectChat(e.target.value)}
            className="max-w-40 rounded-lg border border-line bg-panel px-2 py-1.5 text-xs outline-none"
          >
            {chats.map((c) => (
              <option key={c.id} value={c.id}>
                {c.title}
              </option>
            ))}
          </select>
          <button
            onClick={newChat}
            className="rounded-lg border border-line px-2.5 py-1.5 text-xs font-semibold hover:border-brand"
          >
            + New
          </button>
          <div className="flex-1" />
          <button
            onClick={() => setView(view === "chat" ? "templates" : "chat")}
            className={`rounded-lg px-2.5 py-1.5 text-xs font-semibold ${
              view === "templates" ? "bg-brand text-white" : "border border-line hover:border-brand"
            }`}
          >
            Templates
          </button>
          <button
            onClick={() => setShowSettings(true)}
            className="rounded-lg border border-line px-2.5 py-1.5 text-xs font-semibold hover:border-brand"
            title="Settings"
          >
            ⚙
          </button>
        </header>

        {view === "templates" ? (
          <Templates
            onPersonalize={(name) => {
              setView("chat");
              setInput(
                `Personalize the "${name}" template for me — adapt it to my profile, 1RMs, and readiness, then generate the program.`,
              );
            }}
          />
        ) : (
          <>
            <div className="flex-1 space-y-4 overflow-y-auto px-6 py-6">
              {msgs.length === 0 && (
                <div className="mt-24 text-center text-mut">
                  <p className="text-lg">What are we training for?</p>
                  <p className="mt-2 text-sm">
                    Ask for a program, log a session, check in — or attach physique photos with 📎 for
                    an honest assessment.
                  </p>
                </div>
              )}
              {msgs.map((m, i) => (
                <div key={i} className={m.role === "user" ? "flex justify-end" : "flex"}>
                  <div
                    className={
                      m.role === "user"
                        ? "max-w-[70%] rounded-2xl rounded-br-sm bg-brand/90 px-4 py-2.5 text-white"
                        : "max-w-[85%] rounded-2xl rounded-bl-sm bg-panel px-4 py-2.5"
                    }
                    dangerouslySetInnerHTML={md(m.text || (busy && i === msgs.length - 1 ? "…" : ""))}
                  />
                </div>
              ))}
              <div ref={bottomRef} />
            </div>

            <footer className="border-t border-line p-4">
              {images.length > 0 && (
                <div className="mb-2 flex gap-2">
                  {images.map((u, i) => (
                    <div key={i} className="relative">
                      <img src={u} className="h-14 w-14 rounded-lg object-cover" />
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
                  className="rounded-xl border border-line px-3 text-lg hover:border-brand"
                >
                  📎
                </button>
                <input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && send()}
                  placeholder="Log a session, ask for a program, attach photos…"
                  className="flex-1 rounded-xl border border-line bg-panel px-4 py-3 outline-none placeholder:text-mut focus:border-brand"
                />
                <button
                  onClick={send}
                  disabled={busy}
                  className="rounded-xl bg-brand px-5 font-semibold text-white disabled:opacity-40"
                >
                  Send
                </button>
              </div>
            </footer>
          </>
        )}
      </main>

      {/* ===== Sidebar ===== */}
      <aside className="hidden w-80 flex-col gap-4 overflow-y-auto border-l border-line p-5 lg:flex">
        <section className="rounded-xl bg-panel p-4">
          <h3 className="mb-2 text-xs font-semibold uppercase tracking-wider text-mut">Training Load</h3>
          <div className="text-3xl font-black">
            {acwr ?? "—"} <span className={`text-sm font-semibold ${tone.cls}`}>{tone.label}</span>
          </div>
          <p className="mt-1 text-xs text-mut">ACWR · {dash?.load?.sessions_28d ?? 0} sessions / 28d</p>
        </section>

        <section className="rounded-xl bg-panel p-4">
          <h3 className="mb-2 text-xs font-semibold uppercase tracking-wider text-mut">
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
          <section className="rounded-xl bg-panel p-4">
            <h3 className="mb-2 text-xs font-semibold uppercase tracking-wider text-mut">1RMs</h3>
            <ul className="space-y-1 text-sm">
              {Object.entries(oneRms).map(([lift, kg]) => (
                <li key={lift} className="flex justify-between">
                  <span className="text-mut">{lift}</span>
                  <span className="font-semibold">{kg} kg</span>
                </li>
              ))}
            </ul>
          </section>
        )}

        <FormLookup />

        <section className="rounded-xl bg-panel p-4">
          <h3 className="mb-2 text-xs font-semibold uppercase tracking-wider text-mut">Programs</h3>
          {dash?.programs?.length ? (
            <ul className="space-y-2">
              {dash.programs.map((p) => (
                <li key={p.id}>
                  <a
                    href={keyed(`/api/programs/${p.id}/pdf`)}
                    target="_blank"
                    className="block rounded-lg border border-line px-3 py-2 text-sm hover:border-brand"
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
      </aside>

      {showSettings && (
        <Settings
          profile={profile as Record<string, unknown>}
          onClose={() => setShowSettings(false)}
          onSaved={refreshDash}
        />
      )}
    </div>
  );
}

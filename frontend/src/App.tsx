import { useEffect, useRef, useState } from "react";

type Msg = { role: "user" | "assistant"; text: string };
type Program = { id: string; name: string; goal: string | null; created_at: string };
type Dashboard = {
  profile: Record<string, unknown>;
  readiness: Array<Record<string, unknown> & { date: string }>;
  load: { acwr: number | null; sessions_28d: number };
  programs: Program[];
};

// Minimal markdown: **bold** + [links](url)
function md(text: string) {
  const html = text
    .replace(/&/g, "&amp;").replace(/</g, "&lt;")
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(
      /\[(.+?)\]\((.+?)\)/g,
      '<a href="$2" target="_blank" class="text-brand underline">$1</a>',
    )
    .replace(/\n/g, "<br/>");
  return { __html: html };
}

function acwrTone(acwr: number | null) {
  if (acwr == null) return { label: "no data", cls: "text-mut" };
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
  const bottomRef = useRef<HTMLDivElement>(null);

  const refreshDash = () =>
    fetch("/api/dashboard").then((r) => r.json()).then(setDash).catch(() => {});

  useEffect(() => { refreshDash(); }, []);
  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth" }); }, [msgs]);

  async function send() {
    const message = input.trim();
    if (!message || busy) return;
    setInput("");
    setBusy(true);
    setMsgs((m) => [...m, { role: "user", text: message }, { role: "assistant", text: "" }]);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
      });
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
        }
      }
    } catch {
      setMsgs((m) => [...m.slice(0, -1), { role: "assistant", text: "⚠ backend unreachable" }]);
    } finally {
      setBusy(false);
      refreshDash();
    }
  }

  const today = dash?.readiness?.[0];
  const acwr = dash?.load?.acwr ?? null;
  const tone = acwrTone(acwr);
  const oneRms = (dash?.profile?.one_rms ?? {}) as Record<string, number>;

  return (
    <div className="flex h-full">
      {/* ===== Chat ===== */}
      <main className="flex flex-1 flex-col">
        <header className="border-b border-line px-6 py-4">
          <span className="font-black tracking-[0.3em] text-brand">COACH K</span>
          <span className="ml-3 text-xs text-mut">science-grounded strength coaching</span>
        </header>

        <div className="flex-1 space-y-4 overflow-y-auto px-6 py-6">
          {msgs.length === 0 && (
            <div className="mt-24 text-center text-mut">
              <p className="text-lg">What are we training for?</p>
              <p className="mt-2 text-sm">
                Ask for a program, log a session, or just check in.
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
          <div className="flex gap-2">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && send()}
              placeholder="Log a session, ask for a program, report how you feel…"
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
      </main>

      {/* ===== Sidebar ===== */}
      <aside className="hidden w-80 flex-col gap-4 overflow-y-auto border-l border-line p-5 lg:flex">
        <section className="rounded-xl bg-panel p-4">
          <h3 className="mb-2 text-xs font-semibold uppercase tracking-wider text-mut">
            Training Load
          </h3>
          <div className="text-3xl font-black">
            {acwr ?? "—"} <span className={`text-sm font-semibold ${tone.cls}`}>{tone.label}</span>
          </div>
          <p className="mt-1 text-xs text-mut">
            ACWR · {dash?.load?.sessions_28d ?? 0} sessions / 28d
          </p>
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
            <h3 className="mb-2 text-xs font-semibold uppercase tracking-wider text-mut">
              1RMs
            </h3>
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

        <section className="rounded-xl bg-panel p-4">
          <h3 className="mb-2 text-xs font-semibold uppercase tracking-wider text-mut">
            Programs
          </h3>
          {dash?.programs?.length ? (
            <ul className="space-y-2">
              {dash.programs.map((p) => (
                <li key={p.id}>
                  <a
                    href={`/api/programs/${p.id}/pdf`}
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
    </div>
  );
}

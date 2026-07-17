import { useState } from "react";
import { api } from "./api";

type Props = {
  profile: Record<string, unknown>;
  onClose: () => void;
  onSaved: () => void;
};

const LIFTS = ["squat", "bench", "deadlift", "press"] as const;

export default function Settings({ profile, onClose, onSaved }: Props) {
  const rms = (profile.lifts_1rm ?? {}) as Record<string, number>;
  const [form, setForm] = useState({
    name: String(profile.name ?? ""),
    goals: String(profile.goals ?? ""),
    schedule: String(profile.schedule ?? ""),
    equipment: String(profile.equipment ?? ""),
    bodyweight_kg: profile.bodyweight_kg ? String(profile.bodyweight_kg) : "",
    ...Object.fromEntries(LIFTS.map((l) => [l, rms[l] ? String(rms[l]) : ""])),
  } as Record<string, string>);
  const [saving, setSaving] = useState(false);

  async function save() {
    setSaving(true);
    const lifts: Record<string, number> = {};
    for (const l of LIFTS) if (form[l]) lifts[l] = Number(form[l]);
    const patch: Record<string, unknown> = {
      name: form.name || undefined,
      goals: form.goals || undefined,
      schedule: form.schedule || undefined,
      equipment: form.equipment || undefined,
      bodyweight_kg: form.bodyweight_kg ? Number(form.bodyweight_kg) : undefined,
      ...(Object.keys(lifts).length ? { lifts_1rm: lifts } : {}),
    };
    await api("/api/profile", {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ patch }),
    });
    setSaving(false);
    onSaved();
    onClose();
  }

  const field = (key: string, label: string, placeholder = "") => (
    <label className="block">
      <span className="mb-1 block text-xs font-semibold uppercase tracking-wider text-mut">{label}</span>
      <input
        value={form[key]}
        onChange={(e) => setForm({ ...form, [key]: e.target.value })}
        placeholder={placeholder}
        className="w-full rounded-lg border border-line bg-ink px-3 py-2 text-sm outline-none focus:border-brand"
      />
    </label>
  );

  return (
    <div className="fixed inset-0 z-40 flex items-center justify-center bg-ink/90 p-4" onClick={onClose}>
      <div
        className="max-h-[90vh] w-full max-w-md overflow-y-auto rounded-2xl bg-panel p-6"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-black">Settings — Athlete Profile</h2>
          <button onClick={onClose} className="text-mut hover:text-white">✕</button>
        </div>
        <div className="space-y-3">
          {field("name", "Name")}
          {field("goals", "Goals", "e.g. 200kg squat; size secondary")}
          {field("schedule", "Schedule", "e.g. 3 days/week")}
          {field("equipment", "Equipment", "e.g. full barbell setup at home")}
          {field("bodyweight_kg", "Bodyweight (kg)", "e.g. 84")}
          <div>
            <span className="mb-1 block text-xs font-semibold uppercase tracking-wider text-mut">1RMs (kg)</span>
            <div className="grid grid-cols-2 gap-2">
              {LIFTS.map((l) => (
                <input
                  key={l}
                  value={form[l]}
                  onChange={(e) => setForm({ ...form, [l]: e.target.value })}
                  placeholder={l}
                  className="rounded-lg border border-line bg-ink px-3 py-2 text-sm outline-none focus:border-brand"
                />
              ))}
            </div>
          </div>
        </div>
        <button
          onClick={save}
          disabled={saving}
          className="mt-5 w-full rounded-xl bg-brand py-2.5 font-semibold text-white disabled:opacity-40"
        >
          {saving ? "Saving…" : "Save profile"}
        </button>
        <p className="mt-3 text-xs text-mut">
          Coach K also updates this automatically from your chats — edits here take effect immediately.
        </p>
      </div>
    </div>
  );
}

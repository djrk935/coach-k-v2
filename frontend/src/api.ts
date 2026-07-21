// Shared API helpers + types.

export const appKey = () => localStorage.getItem("coachk_key") ?? "";
export const api = (path: string, init: RequestInit = {}) =>
  fetch(path, { ...init, headers: { ...init.headers, "x-app-key": appKey() } });
export const keyed = (url: string) =>
  appKey() ? `${url}${url.includes("?") ? "&" : "?"}key=${encodeURIComponent(appKey())}` : url;

// Downscale client-side so photo payloads stay sane (and cheap to analyze).
export async function fileToDataUrl(file: File, maxDim = 1280): Promise<string> {
  const img = document.createElement("img");
  const url = URL.createObjectURL(file);
  await new Promise((res, rej) => {
    img.onload = res;
    img.onerror = rej;
    img.src = url;
  });
  const scale = Math.min(1, maxDim / Math.max(img.width, img.height));
  const canvas = document.createElement("canvas");
  canvas.width = Math.round(img.width * scale);
  canvas.height = Math.round(img.height * scale);
  canvas.getContext("2d")!.drawImage(img, 0, 0, canvas.width, canvas.height);
  URL.revokeObjectURL(url);
  return canvas.toDataURL("image/jpeg", 0.85);
}

function urlBase64ToUint8Array(base64: string): BufferSource {
  const padding = "=".repeat((4 - (base64.length % 4)) % 4);
  const b64 = (base64 + padding).replace(/-/g, "+").replace(/_/g, "/");
  const raw = atob(b64);
  const buf = new ArrayBuffer(raw.length);
  const view = new Uint8Array(buf);
  for (let i = 0; i < raw.length; i++) view[i] = raw.charCodeAt(i);
  return buf;
}

// Proactive coaching: ask permission, subscribe to push, register with the server.
// Returns a status the caller can show — never throws.
export async function enablePush(): Promise<"enabled" | "denied" | "unsupported" | "unconfigured"> {
  if (!("serviceWorker" in navigator) || !("PushManager" in window)) return "unsupported";
  const keyRes = await api("/api/push/vapid-public-key");
  const { key } = keyRes.ok ? await keyRes.json() : { key: null };
  if (!key) return "unconfigured";

  const perm = await Notification.requestPermission();
  if (perm !== "granted") return "denied";

  const reg = await navigator.serviceWorker.ready;
  const existing = await reg.pushManager.getSubscription();
  const sub =
    existing ??
    (await reg.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: urlBase64ToUint8Array(key),
    }));
  await api("/api/push/subscribe", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ subscription: sub.toJSON() }),
  });
  return "enabled";
}

export type Msg = { role: "user" | "assistant"; text: string };
export type ChatMeta = { id: string; title: string; created_at: string };
export type Program = { id: string; name: string; goal: string | null; created_at: string };
export type Dashboard = {
  profile: Record<string, unknown>;
  readiness: Array<Record<string, unknown> & { date: string }>;
  load: { acwr: number | null; sessions_28d: number };
  programs: Program[];
};
export type LoggedSet = {
  exercise: string; set_index: number; weight_lbs: number | null;
  reps: number | null; rir: number | null; is_pr: boolean;
};
export type WarmupSet = {
  weight_lbs: number | null;
  reps: number;
  pct: number | null;
  label: string;
};
export type TodayExercise = {
  exercise: string; sets: number; reps: string; intensity: string;
  tempo: string | null; rest_s: number | null; notes: string | null;
  set_type: string; superset_group: string | null;
  suggested_weight_lbs: number | null; logged_sets: LoggedSet[]; image_urls: string[];
  form_cue?: string | null;
  swap_suggestion?: string | null;
  progression?: { delta_lbs: number; reason: string } | null;
  adapted?: boolean;
  swapped?: boolean;
  warmup_sets?: WarmupSet[];
};
export type TodayAdaptation = {
  score: number | null;
  status: string;
  volume_scale: number;
  soft_day: boolean;
  intensity_note: string;
  reasons: string[];
  needs_checkin: boolean;
};
export type InjuryProtocol = {
  region: string;
  region_key: string;
  steps: string[];
  alternatives: string[];
  volume_hint?: string;
};
export type TodayPlan = {
  active: boolean;
  program_id: string; program_name: string; day_index: number; cycle_count: number;
  day_label: string; focus: string; exercises: TodayExercise[]; workout_id: string | null;
  adaptation?: TodayAdaptation;
  catch_up?: { days_missed: number; options: string[]; message: string } | null;
  goal_mode?: string | null;
  nutrition_targets?: Record<string, unknown> | null;
  pain_regions?: string[];
  injury_protocols?: InjuryProtocol[];
  pain_region_options?: { key: string; label: string }[];
  travel?: boolean;
  debrief?: { headline: string; message: string; completion_pct: number; prs: string[] };
};

export type TemplateEx = {
  name: string; sets: number; reps: string; intensity: string; image_urls: string[];
};
export type Template = {
  id: string; name: string; goal: string; days_per_week: number;
  summary: string; based_on: string; source_type?: string;
  days: { label: string; exercises: TemplateEx[] }[];
};

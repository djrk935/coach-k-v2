// Shared API helpers + types.

export const appKey = () => localStorage.getItem("coachk_key") ?? "";
export const api = (path: string, init: RequestInit = {}) =>
  fetch(path, { ...init, headers: { ...(init.headers ?? {}), "x-app-key": appKey() } });
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

export type Msg = { role: "user" | "assistant"; text: string };
export type ChatMeta = { id: string; title: string; created_at: string };
export type Program = { id: string; name: string; goal: string | null; created_at: string };
export type Dashboard = {
  profile: Record<string, unknown>;
  readiness: Array<Record<string, unknown> & { date: string }>;
  load: { acwr: number | null; sessions_28d: number };
  programs: Program[];
};
export type TemplateEx = {
  name: string; sets: number; reps: string; intensity: string; image_urls: string[];
};
export type Template = {
  id: string; name: string; goal: string; days_per_week: number;
  summary: string; based_on: string;
  days: { label: string; exercises: TemplateEx[] }[];
};

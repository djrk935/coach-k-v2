/** Signal Strip background theme — paper (light) or dark. */

export type BgTheme = "light" | "dark";

export const THEME_KEY = "coachk_theme";

export function readTheme(): BgTheme {
  try {
    const v = localStorage.getItem(THEME_KEY);
    if (v === "dark" || v === "light") return v;
  } catch {
    /* ignore */
  }
  return "light";
}

export function applyTheme(theme: BgTheme) {
  document.documentElement.setAttribute("data-theme", theme);
  const meta = document.querySelector('meta[name="theme-color"]');
  if (meta) meta.setAttribute("content", theme === "dark" ? "#0a0a0a" : "#e11d2e");
}

export function setTheme(theme: BgTheme) {
  try {
    localStorage.setItem(THEME_KEY, theme);
  } catch {
    /* ignore */
  }
  applyTheme(theme);
}

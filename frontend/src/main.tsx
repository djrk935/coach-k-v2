import { createRoot } from "react-dom/client";
import App from "./App";
import { initPwaInstall } from "./pwaInstall";
import { applyTheme, readTheme } from "./theme";
import "./index.css";

applyTheme(readTheme());
initPwaInstall();

if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("/sw.js").catch(() => {});
  });
}

createRoot(document.getElementById("root")!).render(<App />);

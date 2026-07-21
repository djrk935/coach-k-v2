import { createRoot } from "react-dom/client";
import App from "./App";
import { initPwaInstall } from "./pwaInstall";
import "./index.css";

initPwaInstall();

if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("/sw.js").catch(() => {});
  });
}

createRoot(document.getElementById("root")!).render(<App />);

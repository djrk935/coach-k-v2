import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    // Harness-assigned port when launched via preview (autoPort), else 5173.
    port: Number(process.env.PORT) || 5173,
    proxy: { "/api": "http://localhost:8000" },
  },
});

import { useEffect, useState } from "react";

/** Thin connectivity strip — coaching data still needs the network. */
export default function OfflineBanner() {
  const [offline, setOffline] = useState(
    typeof navigator !== "undefined" ? !navigator.onLine : false,
  );

  useEffect(() => {
    const goOff = () => setOffline(true);
    const goOn = () => setOffline(false);
    window.addEventListener("offline", goOff);
    window.addEventListener("online", goOn);
    return () => {
      window.removeEventListener("offline", goOff);
      window.removeEventListener("online", goOn);
    };
  }, []);

  if (!offline) return null;

  return (
    <div
      role="status"
      className="border-b border-amber-500/30 bg-amber-500/15 px-4 py-2 text-center text-[11px] font-semibold text-amber-100"
    >
      You&apos;re offline — the app shell stays available. Live coaching syncs when you reconnect.
    </div>
  );
}

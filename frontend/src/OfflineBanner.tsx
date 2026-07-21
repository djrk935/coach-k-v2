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
      className="bg-brand px-4 py-2 text-center text-[11px] font-bold uppercase tracking-[0.18em] text-white"
    >
      Offline — shell stays available. Coaching syncs when you reconnect.
    </div>
  );
}

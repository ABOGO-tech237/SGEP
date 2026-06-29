"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { RefreshCw } from "lucide-react";

export function RetryButton() {
  const router = useRouter();
  const [retrying, setRetrying] = useState(false);

  function handleRetry() {
    setRetrying(true);
    router.refresh();
    // refresh() is synchronous — reset spinner after a short delay
    setTimeout(() => setRetrying(false), 2000);
  }

  return (
    <button
      onClick={handleRetry}
      disabled={retrying}
      className="inline-flex items-center gap-1.5 rounded-md bg-amber-600 px-3 py-1.5 text-xs font-medium text-white transition hover:bg-amber-700 disabled:cursor-not-allowed disabled:opacity-60"
    >
      <RefreshCw className={`size-3.5 ${retrying ? "animate-spin" : ""}`} />
      {retrying ? "Refreshing…" : "Try again"}
    </button>
  );
}

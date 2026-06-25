"use client";

import { useCallback, useEffect, useState } from "react";
import { Loader2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import type { ReportJobStatus } from "@/lib/types/reports";

interface ExportJobPollerProps {
  jobId: string;
  label: string;
  statusPath?: "reports" | "report-cards";
  onComplete?: () => void;
}

export function ExportJobPoller({
  jobId,
  label,
  statusPath = "reports",
  onComplete,
}: ExportJobPollerProps) {
  const [status, setStatus] = useState<ReportJobStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    let cancelled = false;
    let attempts = 0;
    const maxAttempts = 60;

    async function poll() {
      while (!cancelled && attempts < maxAttempts) {
        attempts += 1;
        try {
          const response = await fetch(`/api/admin/${statusPath}/${jobId}/status`);
          const payload = (await response.json()) as ReportJobStatus & { error?: string };
          if (!response.ok) {
            setError(payload.error ?? "Unable to check export status.");
            return;
          }
          setStatus(payload);
          if (payload.status === "completed" || payload.status === "done") {
            onComplete?.();
            return;
          }
          if (payload.status === "failed" || payload.status === "error") {
            setError(payload.error ?? "Export failed.");
            return;
          }
        } catch {
          setError("Unable to check export status.");
          return;
        }
        await new Promise((resolve) => setTimeout(resolve, 2000));
      }
      if (!cancelled) {
        setError("Export timed out. Try again later.");
      }
    }

    void poll();
    return () => {
      cancelled = true;
    };
  }, [jobId, statusPath, onComplete]);

  const download = useCallback(async () => {
    setDownloading(true);
    setError(null);
    try {
      const response = await fetch(`/api/admin/${statusPath}/${jobId}/download`);
      if (!response.ok) {
        const payload = (await response.json().catch(() => null)) as { error?: string } | null;
        throw new Error(payload?.error ?? "Download failed.");
      }
      const blob = await response.blob();
      const disposition = response.headers.get("content-disposition");
      const filenameMatch = disposition?.match(/filename="?([^"]+)"?/);
      const filename = filenameMatch?.[1] ?? `${label.replace(/\s+/g, "-").toLowerCase()}.bin`;
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = filename;
      anchor.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Download failed.");
    } finally {
      setDownloading(false);
    }
  }, [jobId, label, statusPath]);

  const isReady = status?.status === "completed" || status?.status === "done";

  return (
    <div className="rounded-lg border border-border bg-muted/30 px-4 py-3 text-sm space-y-2">
      <div className="flex items-center justify-between gap-3">
        <span className="font-medium">{label}</span>
        <span className="text-xs text-muted-foreground capitalize">
          {status?.status ?? "pending"}
        </span>
      </div>
      {!isReady && !error ? (
        <p className="flex items-center gap-2 text-xs text-muted-foreground">
          <Loader2 className="size-3.5 animate-spin" />
          Processing export…
        </p>
      ) : null}
      {error ? <p className="text-xs text-destructive">{error}</p> : null}
      {isReady ? (
        <Button type="button" size="sm" disabled={downloading} onClick={() => void download()}>
          {downloading ? "Downloading…" : "Download file"}
        </Button>
      ) : null}
    </div>
  );
}

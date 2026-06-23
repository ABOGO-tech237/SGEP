"use client";

import { useState } from "react";
import { Download } from "lucide-react";
import { cn } from "@/lib/utils";

interface PdfDownloadProps {
  href: string;
  filename?: string;
  label?: string;
  params?: Record<string, string>;
  className?: string;
}

export function PdfDownload({
  href,
  filename = "document.pdf",
  label = "Download PDF",
  params,
  className,
}: PdfDownloadProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleDownload() {
    setIsLoading(true);
    setError(null);
    try {
      const url = params
        ? `${href}?${new URLSearchParams(params).toString()}`
        : href;
      const res = await fetch(url);
      if (!res.ok) throw new Error(`Request failed: ${res.status}`);
      const blob = await res.blob();
      const objectUrl = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = objectUrl;
      anchor.download = filename;
      anchor.click();
      URL.revokeObjectURL(objectUrl);
    } catch {
      setError("Download failed. Please try again.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="inline-flex flex-col items-start gap-1">
      <button
        type="button"
        onClick={handleDownload}
        disabled={isLoading}
        aria-busy={isLoading}
        className={cn(
          "inline-flex items-center gap-2 rounded-md border border-input bg-background px-3 py-2 text-sm font-medium transition hover:bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50",
          className
        )}
      >
        <Download className="size-4" aria-hidden />
        {isLoading ? "Downloading…" : label}
      </button>
      {error && (
        <p role="alert" className="text-xs text-destructive">
          {error}
        </p>
      )}
    </div>
  );
}

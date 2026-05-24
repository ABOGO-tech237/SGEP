"use client";

import { AlertTriangle } from "lucide-react";

interface SuspendedBannerProps {
  isSuspended: boolean;
  children: React.ReactNode;
  reason?: string;
}

export function SuspendedBanner({
  isSuspended,
  children,
  reason,
}: SuspendedBannerProps) {
  if (!isSuspended) return <>{children}</>;

  return (
    <div className="flex flex-col gap-4">
      <div
        role="alert"
        aria-live="assertive"
        className="flex items-start gap-3 rounded-lg border border-destructive/50 bg-destructive/10 p-4"
      >
        <AlertTriangle
          className="mt-0.5 size-5 shrink-0 text-destructive"
          aria-hidden
        />
        <div>
          <p className="font-semibold text-destructive">Account suspended</p>
          {reason && (
            <p className="mt-1 text-sm text-destructive/80">{reason}</p>
          )}
          <p className="mt-1 text-sm text-destructive/80">
            Contact the school administration to restore access.
          </p>
        </div>
      </div>
      <div
        aria-hidden
        inert
        className="pointer-events-none select-none opacity-40"
      >
        {children}
      </div>
    </div>
  );
}

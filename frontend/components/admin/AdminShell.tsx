"use client";

import { useAuth } from "@/context/AuthContext";
import { AdminSidebar } from "@/components/admin/AdminSidebar";

interface AdminShellProps {
  title: string;
  description?: string;
  actions?: React.ReactNode;
  children: React.ReactNode;
}

function getInitials(name: string): string {
  const parts = name.trim().split(/\s+/).filter(Boolean);
  if (parts.length === 0) return "AD";
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return `${parts[0][0]}${parts[parts.length - 1][0]}`.toUpperCase();
}

export function AdminShell({
  title,
  description,
  actions,
  children,
}: AdminShellProps) {
  const { user } = useAuth();
  const initials = getInitials(user?.name ?? "Admin");

  return (
    <div className="flex min-h-screen bg-background text-foreground overflow-hidden">
      <AdminSidebar />

      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="flex items-center justify-between px-6 py-4 border-b border-border bg-card shrink-0">
          <div>
            <h1 className="text-lg font-semibold">{title}</h1>
            {description ? (
              <p className="text-xs text-muted-foreground">{description}</p>
            ) : null}
          </div>
          <div className="flex items-center gap-3">
            {actions}
            <div
              className="size-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xs font-semibold"
              aria-label={user?.name ?? "Admin user"}
              title={user?.name ?? "Admin"}
            >
              {initials}
            </div>
          </div>
        </header>

        <main className="flex-1 overflow-y-auto px-6 py-6">{children}</main>
      </div>
    </div>
  );
}

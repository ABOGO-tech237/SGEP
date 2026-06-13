import { headers } from "next/headers";
import {
  Bell,
  BookOpen,
  ChevronRight,
  FileText,
  GraduationCap,
  LayoutDashboard,
  LogOut,
  Settings,
  TrendingUp,
  UserCheck,
  Users,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { StatusBadge } from "@/components/ui/StatusBadge";
import type { AdminDashboardResponse } from "@/lib/types/admin";

export const dynamic = "force-dynamic";

const STAT_DECORATIONS = {
  "Total Students": {
    icon: GraduationCap,
    color: "bg-blue-50 text-blue-600 dark:bg-blue-900/20 dark:text-blue-400",
  },
  "Active Students": {
    icon: Users,
    color:
      "bg-violet-50 text-violet-600 dark:bg-violet-900/20 dark:text-violet-400",
  },
  "Inactive Students": {
    icon: TrendingUp,
    color:
      "bg-emerald-50 text-emerald-600 dark:bg-emerald-900/20 dark:text-emerald-400",
  },
  "Classes Represented": {
    icon: BookOpen,
    color:
      "bg-amber-50 text-amber-600 dark:bg-amber-900/20 dark:text-amber-400",
  },
} as const;

const navItems = [
  { label: "Dashboard", icon: LayoutDashboard, active: true },
  { label: "Students", icon: GraduationCap, active: false },
  { label: "Teachers", icon: UserCheck, active: false },
  { label: "Classes", icon: BookOpen, active: false },
  { label: "Reports", icon: FileText, active: false },
  { label: "Settings", icon: Settings, active: false },
];

async function loadAdminDashboard(): Promise<AdminDashboardResponse | null> {
  const requestHeaders = await headers();
  const host = requestHeaders.get("host");
  if (!host) {
    return null;
  }

  const protocol = requestHeaders.get("x-forwarded-proto") ?? "http";
  const response = await fetch(
    new URL("/api/admin/dashboard", `${protocol}://${host}`),
    {
      cache: "no-store",
    },
  );

  if (!response.ok) {
    return null;
  }

  return (await response.json()) as AdminDashboardResponse;
}

export default async function AdminDashboard() {
  const dashboard = await loadAdminDashboard();

  return (
    <div className="flex h-screen bg-background text-foreground overflow-hidden">
      {/* Sidebar */}
      <aside className="w-60 flex flex-col border-r border-border bg-card shrink-0">
        <div className="px-5 py-5 border-b border-border">
          <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-0.5">
            PSMS
          </p>
          <p className="text-sm font-medium">Admin Portal</p>
        </div>

        <nav className="flex-1 px-3 py-4 space-y-0.5">
          {navItems.map(({ label, icon: Icon, active }) => (
            <button
              key={label}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                active
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground"
              }`}
            >
              <Icon className="size-4 shrink-0" />
              {label}
            </button>
          ))}
        </nav>

        <div className="px-3 py-4 border-t border-border space-y-1">
          <button className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-muted-foreground hover:bg-muted hover:text-foreground transition-colors">
            <Bell className="size-4 shrink-0" />
            Notifications
            <span className="ml-auto bg-destructive text-destructive-foreground text-xs rounded-full px-1.5 py-0.5 font-medium">
              3
            </span>
          </button>
          <button className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-muted-foreground hover:bg-muted hover:text-foreground transition-colors">
            <LogOut className="size-4 shrink-0" />
            Sign out
          </button>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top bar */}
        <header className="flex items-center justify-between px-6 py-4 border-b border-border bg-card shrink-0">
          <div>
            <h1 className="text-lg font-semibold">Dashboard</h1>
            <p className="text-xs text-muted-foreground">
              {dashboard
                ? `Live data synced ${new Date(dashboard.generated_at).toLocaleString("en-GB")}`
                : "Live dashboard unavailable"}
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline" size="sm">
              <FileText className="size-3.5" />
              Export report
            </Button>
            <div className="size-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xs font-semibold">
              AD
            </div>
          </div>
        </header>

        {/* Scrollable body */}
        <main className="flex-1 overflow-y-auto px-6 py-6 space-y-6">
          {!dashboard ? (
            <div className="rounded-xl border border-dashed border-border bg-card/60 px-5 py-4 text-sm text-muted-foreground">
              The admin dashboard data could not be loaded. Check the session
              and backend connection, then refresh.
            </div>
          ) : null}

          {/* Stat cards */}
          <div className="grid grid-cols-4 gap-4">
            {(dashboard?.stats ?? []).map(({ label, value, change, positive }) => {
              const decoration = STAT_DECORATIONS[label as keyof typeof STAT_DECORATIONS];
              const Icon = decoration?.icon ?? TrendingUp;

              return (
                <div
                  key={label}
                  className="rounded-xl border border-border bg-card p-4 flex flex-col gap-3"
                >
                  <div className="flex items-center justify-between">
                    <p className="text-sm text-muted-foreground font-medium">
                      {label}
                    </p>
                    <span
                      className={`size-8 rounded-lg flex items-center justify-center ${decoration?.color ?? "bg-muted text-muted-foreground"}`}
                    >
                      <Icon className="size-4" />
                    </span>
                  </div>
                  <p className="text-2xl font-bold tracking-tight">{value}</p>
                  <p
                    className={`text-xs font-medium ${positive === true ? "text-emerald-600 dark:text-emerald-400" : positive === false ? "text-destructive" : "text-muted-foreground"}`}
                  >
                    {change}
                  </p>
                </div>
              );
            })}
          </div>

          {/* Lower section */}
          <div className="grid grid-cols-3 gap-4">
            {/* Recent activity */}
            <div className="col-span-2 rounded-xl border border-border bg-card">
              <div className="flex items-center justify-between px-5 py-4 border-b border-border">
                <h2 className="text-sm font-semibold">Recent Activity</h2>
                <button className="text-xs text-muted-foreground hover:text-foreground flex items-center gap-0.5 transition-colors">
                  View all <ChevronRight className="size-3" />
                </button>
              </div>
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border">
                    <th className="px-5 py-2.5 text-left text-xs font-medium text-muted-foreground">
                      Student
                    </th>
                    <th className="px-5 py-2.5 text-left text-xs font-medium text-muted-foreground">
                      Action
                    </th>
                    <th className="px-5 py-2.5 text-left text-xs font-medium text-muted-foreground">
                      Class
                    </th>
                    <th className="px-5 py-2.5 text-left text-xs font-medium text-muted-foreground">
                      Status
                    </th>
                    <th className="px-5 py-2.5 text-right text-xs font-medium text-muted-foreground">
                      Time
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {(dashboard?.recent_activity ?? []).map(
                    ({ id, name, action, grade, status, time }) => (
                      <tr
                        key={id}
                        className="border-b border-border last:border-0 hover:bg-muted/40 transition-colors"
                      >
                        <td className="px-5 py-3 font-medium">{name}</td>
                        <td className="px-5 py-3 text-muted-foreground">
                          {action}
                        </td>
                        <td className="px-5 py-3 text-muted-foreground">
                          {grade}
                        </td>
                        <td className="px-5 py-3">
                          <StatusBadge status={status} />
                        </td>
                        <td className="px-5 py-3 text-right text-muted-foreground text-xs">
                          {time}
                        </td>
                      </tr>
                    ),
                  )}
                </tbody>
              </table>
            </div>

            {/* Quick actions */}
            <div className="rounded-xl border border-border bg-card">
              <div className="px-5 py-4 border-b border-border">
                <h2 className="text-sm font-semibold">Quick Actions</h2>
              </div>
              <div className="p-4 space-y-2">
                {[
                  { label: "Enrol new student", icon: GraduationCap },
                  { label: "Add teacher", icon: UserCheck },
                  { label: "Create class", icon: BookOpen },
                  { label: "Generate report", icon: FileText },
                  { label: "Manage settings", icon: Settings },
                ].map(({ label, icon: Icon }) => (
                  <button
                    key={label}
                    className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm hover:bg-muted transition-colors text-left"
                  >
                    <Icon className="size-4 text-muted-foreground shrink-0" />
                    {label}
                    <ChevronRight className="size-3.5 ml-auto text-muted-foreground" />
                  </button>
                ))}
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

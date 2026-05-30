import {
  BookOpen,
  ChevronRight,
  FileText,
  GraduationCap,
  LayoutDashboard,
  LogOut,
  Settings,
  ShieldCheck,
  Users,
  UserCheck,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { getAdminDashboard } from "@/lib/admin";
import type { AdminDashboardData, AdminUserSummary } from "@/lib/types/admin";

type StatCard = {
  label: string;
  value: number;
  change: string;
  icon: typeof GraduationCap;
  color: string;
};

const navItems = [
  { label: "Dashboard", icon: LayoutDashboard, active: true },
  { label: "Students", icon: GraduationCap, active: false },
  { label: "Teachers", icon: UserCheck, active: false },
  { label: "Classes", icon: BookOpen, active: false },
  { label: "Reports", icon: FileText, active: false },
  { label: "Settings", icon: Settings, active: false },
];

function formatName(user: AdminUserSummary): string {
  const fullName = [user.first_name, user.last_name].filter(Boolean).join(" ").trim();
  return user.name || fullName || user.email;
}

function formatRole(role: string): string {
  return role
    .split("_")
    .map((segment) => segment.charAt(0).toUpperCase() + segment.slice(1).toLowerCase())
    .join(" ");
}

function formatDate(value: string): string {
  if (!value) return "N/A";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat("fr-FR", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(date);
}

function buildCards(data: AdminDashboardData): StatCard[] {
  return [
    {
      label: "Total Accounts",
      value: data.total_users,
      change: "Synced from Appwrite",
      icon: Users,
      color: "bg-blue-50 text-blue-600 dark:bg-blue-900/20 dark:text-blue-400",
    },
    {
      label: "Active Accounts",
      value: data.active_users,
      change: "Ready for login",
      icon: ShieldCheck,
      color:
        "bg-emerald-50 text-emerald-600 dark:bg-emerald-900/20 dark:text-emerald-400",
    },
    {
      label: "Superadmins",
      value: data.superadmins,
      change: "Full administrative access",
      icon: LayoutDashboard,
      color:
        "bg-violet-50 text-violet-600 dark:bg-violet-900/20 dark:text-violet-400",
    },
    {
      label: "Parents",
      value: data.parents,
      change: "Portal accounts linked to learners",
      icon: UserCheck,
      color:
        "bg-amber-50 text-amber-600 dark:bg-amber-900/20 dark:text-amber-400",
    },
  ];
}

export default async function AdminDashboard() {
  let dashboard: AdminDashboardData | null = null;
  let errorMessage: string | null = null;

  try {
    dashboard = await getAdminDashboard();
  } catch (error) {
    errorMessage = error instanceof Error ? error.message : "Unable to load dashboard data.";
  }

  if (!dashboard) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background px-6 text-foreground">
        <div className="max-w-lg rounded-2xl border border-border bg-card p-8 shadow-sm">
          <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground">
            PSMS
          </p>
          <h1 className="mt-3 text-2xl font-semibold">Admin dashboard unavailable</h1>
          <p className="mt-2 text-sm text-muted-foreground">
            {errorMessage ?? "No dashboard data returned from Django/Appwrite."}
          </p>
        </div>
      </div>
    );
  }

  const cards = buildCards(dashboard);

  return (
    <div className="flex min-h-screen bg-background text-foreground overflow-hidden">
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
            <LogOut className="size-4 shrink-0" />
            Sign out
          </button>
        </div>
      </aside>

      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="flex items-center justify-between px-6 py-4 border-b border-border bg-card shrink-0">
          <div>
            <h1 className="text-lg font-semibold">Dashboard</h1>
            <p className="text-sm text-muted-foreground">Overview of recent activity and stats</p>  
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

        <main className="flex-1 overflow-y-auto px-6 py-6 space-y-6">
          <div className="grid grid-cols-4 gap-4">
            {cards.map(({ label, value, change, icon: Icon, color }) => (
              <div key={label} className="rounded-xl border border-border bg-card p-4 flex flex-col gap-3">
                <div className="flex items-center justify-between">
                  <p className="text-sm text-muted-foreground font-medium">{label}</p>
                  <span className={`size-8 rounded-lg flex items-center justify-center ${color}`}>
                    <Icon className="size-4" />
                  </span>
                </div>
                <p className="text-2xl font-bold tracking-tight">{value}</p>
                <p className="text-xs font-medium text-muted-foreground">{change}</p>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div className="col-span-2 rounded-xl border border-border bg-card">
              <div className="flex items-center justify-between px-5 py-4 border-b border-border">
                <div>
                  <h2 className="text-sm font-semibold">Recents Users</h2>
                  <p className="text-xs text-muted-foreground mt-1">  Last 5 users</p>
                </div>
                <button className="text-xs text-muted-foreground hover:text-foreground flex items-center gap-0.5 transition-colors">
                  View all <ChevronRight className="size-3" />
                </button>
              </div>

              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border">
                    <th className="px-5 py-2.5 text-left text-xs font-medium text-muted-foreground">Name</th>
                    <th className="px-5 py-2.5 text-left text-xs font-medium text-muted-foreground">Email</th>
                    <th className="px-5 py-2.5 text-left text-xs font-medium text-muted-foreground">Role</th>
                    <th className="px-5 py-2.5 text-left text-xs font-medium text-muted-foreground">Status</th>
                    <th className="px-5 py-2.5 text-right text-xs font-medium text-muted-foreground">Created</th>
                  </tr>
                </thead>
                <tbody>
                  {dashboard.recent_users.map((user) => (
                    <tr key={user.id} className="border-b border-border last:border-0 hover:bg-muted/40 transition-colors">
                      <td className="px-5 py-3 font-medium">{formatName(user)}</td>
                      <td className="px-5 py-3 text-muted-foreground">{user.email}</td>
                      <td className="px-5 py-3 text-muted-foreground">{formatRole(user.role)}</td>
                      <td className="px-5 py-3">
                        <StatusBadge status={user.account_status.toUpperCase() as "ACTIVE" | "SUSPENDED" | "PENDING" | "PAID" | "OVERDUE"} />
                      </td>
                      <td className="px-5 py-3 text-right text-muted-foreground text-xs">
                        {formatDate(user.created_at)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="rounded-xl border border-border bg-card">
              <div className="px-5 py-4 border-b border-border">
                <h2 className="text-sm font-semibold">Quick Actions</h2>
                <p className="text-xs text-muted-foreground mt-1">
                  Use the backend seeding command to insert sample Appwrite users.
                </p>
              </div>
              <div className="p-4 space-y-2">
                {[
                  { label: "Create admin users", icon: GraduationCap },
                  { label: "Create comptable account", icon: UserCheck },
                  { label: "Refresh dashboard", icon: LayoutDashboard },
                  { label: "Export report", icon: FileText },
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
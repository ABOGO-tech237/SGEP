import Link from "next/link";
import {
  ChevronRight,
  FileText,
  GraduationCap,
  LayoutDashboard,
  TrendingUp,
  UserCheck,
  Users,
} from "lucide-react";

import { AdminShell } from "@/components/admin/AdminShell";
import { Button } from "@/components/ui/button";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { serverApiFetch } from "@/lib/server/server-fetch";
import type { AdminDashboardResponse } from "@/lib/types/admin";

export const dynamic = "force-dynamic";

const STAT_DECORATIONS = {
  "Total Users": {
    icon: Users,
    color: "bg-blue-50 text-blue-600 dark:bg-blue-900/20 dark:text-blue-400",
  },
  "Active Users": {
    icon: GraduationCap,
    color: "bg-violet-50 text-violet-600 dark:bg-violet-900/20 dark:text-violet-400",
  },
  Superadmins: {
    icon: UserCheck,
    color: "bg-amber-50 text-amber-600 dark:bg-amber-900/20 dark:text-amber-400",
  },
  Parents: {
    icon: TrendingUp,
    color: "bg-emerald-50 text-emerald-600 dark:bg-emerald-900/20 dark:text-emerald-400",
  },
} as const;

function formatRole(role: string): string {
  const labels: Record<string, string> = {
    superadmin: "Superadmin",
    comptable: "Accountant",
    parent: "Parent",
  };
  return labels[role] ?? role;
}

function mapAccountStatus(status: string): "ACTIVE" | "SUSPENDED" | "PENDING" {
  if (status === "active") return "ACTIVE";
  if (status === "suspended") return "SUSPENDED";
  return "PENDING";
}

export default async function AdminDashboardPage() {
  const dashboard = await serverApiFetch<AdminDashboardResponse>("/api/admin/dashboard");
  const recentUsers = dashboard?.recent_users ?? [];

  return (
    <AdminShell
      title="Dashboard"
      description={
        dashboard
          ? `Live data synced ${new Date(dashboard.generated_at).toLocaleString("en-GB")}`
          : "Live dashboard unavailable"
      }
      actions={
        <Link href="/admin/reports">
          <Button variant="outline" size="sm">
            <FileText className="size-3.5" />
            Export report
          </Button>
        </Link>
      }
    >
      {!dashboard ? (
        <div className="rounded-xl border border-dashed border-border bg-card/60 px-5 py-4 text-sm text-muted-foreground">
          The admin dashboard data could not be loaded. Check the session and
          backend connection, then refresh.
        </div>
      ) : null}

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
        {(dashboard?.stats ?? []).map(({ label, value, change, positive }) => {
          const decoration = STAT_DECORATIONS[label as keyof typeof STAT_DECORATIONS];
          const Icon = decoration?.icon ?? TrendingUp;

          return (
            <div
              key={label}
              className="rounded-xl border border-border bg-card p-4 flex flex-col gap-3"
            >
              <div className="flex items-center justify-between">
                <p className="text-sm text-muted-foreground font-medium">{label}</p>
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

      <div className="mt-6 grid grid-cols-1 xl:grid-cols-3 gap-4">
        <div className="xl:col-span-2 rounded-xl border border-border bg-card">
          <div className="flex items-center justify-between px-5 py-4 border-b border-border">
            <div>
              <h2 className="text-sm font-semibold">Recent users</h2>
              <p className="text-xs text-muted-foreground mt-1">Last 5 accounts</p>
            </div>
            <Link
              href="/admin/settings"
              className="text-xs text-muted-foreground hover:text-foreground flex items-center gap-0.5 transition-colors"
            >
              Settings <ChevronRight className="size-3" />
            </Link>
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
              {recentUsers.map((user) => (
                <tr
                  key={user.id}
                  className="border-b border-border last:border-0 hover:bg-muted/40 transition-colors"
                >
                  <td className="px-5 py-3 font-medium">{user.name || user.email}</td>
                  <td className="px-5 py-3 text-muted-foreground">{user.email}</td>
                  <td className="px-5 py-3 text-muted-foreground">{formatRole(user.role)}</td>
                  <td className="px-5 py-3">
                    <StatusBadge status={mapAccountStatus(user.account_status)} />
                  </td>
                  <td className="px-5 py-3 text-right text-muted-foreground text-xs">
                    {user.created_at
                      ? new Date(user.created_at).toLocaleDateString("en-GB")
                      : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="rounded-xl border border-border bg-card">
          <div className="px-5 py-4 border-b border-border">
            <h2 className="text-sm font-semibold">Quick actions</h2>
            <p className="text-xs text-muted-foreground mt-1">
              Common admin workflows
            </p>
          </div>
          <div className="p-4 space-y-2">
            {[
              { label: "Add student", href: "/admin/students/new", icon: GraduationCap },
              { label: "Manage classes", href: "/admin/classes", icon: LayoutDashboard },
              { label: "Generate reports", href: "/admin/reports", icon: FileText },
              { label: "School settings", href: "/admin/settings", icon: UserCheck },
            ].map(({ label, href, icon: Icon }) => (
              <Link
                key={label}
                href={href}
                className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm hover:bg-muted transition-colors"
              >
                <Icon className="size-4 text-muted-foreground shrink-0" />
                {label}
                <ChevronRight className="size-3.5 ml-auto text-muted-foreground" />
              </Link>
            ))}
          </div>
        </div>
      </div>
    </AdminShell>
  );
}

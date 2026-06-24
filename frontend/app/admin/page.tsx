import {
  GraduationCap,
  Users,
  BookOpen,
  TrendingUp,
  FileText,
  ChevronRight,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { StatusBadge } from "@/components/ui/StatusBadge";

const stats = [
  {
    label: "Total Students",
    value: "1,284",
    change: "+12 this month",
    positive: true,
    icon: GraduationCap,
    color: "bg-blue-50 text-blue-600 dark:bg-blue-900/20 dark:text-blue-400",
  },
  {
    label: "Teaching Staff",
    value: "87",
    change: "+3 this term",
    positive: true,
    icon: Users,
    color:
      "bg-violet-50 text-violet-600 dark:bg-violet-900/20 dark:text-violet-400",
  },
  {
    label: "Active Classes",
    value: "42",
    change: "Across 6 grades",
    positive: null,
    icon: BookOpen,
    color:
      "bg-emerald-50 text-emerald-600 dark:bg-emerald-900/20 dark:text-emerald-400",
  },
  {
    label: "Avg. Attendance",
    value: "94.2%",
    change: "+1.4% vs last week",
    positive: true,
    icon: TrendingUp,
    color:
      "bg-amber-50 text-amber-600 dark:bg-amber-900/20 dark:text-amber-400",
  },
];

const recentActivity = [
  {
    name: "Emily Asante",
    action: "Enrolled",
    grade: "Grade 3B",
    status: "ACTIVE" as const,
    time: "2 min ago",
  },
  {
    name: "Kwame Mensah",
    action: "Fee overdue",
    grade: "Grade 5A",
    status: "OVERDUE" as const,
    time: "1 hr ago",
  },
  {
    name: "Abena Owusu",
    action: "Transfer request",
    grade: "Grade 2C",
    status: "PENDING" as const,
    time: "3 hr ago",
  },
  {
    name: "Kofi Boateng",
    action: "Profile updated",
    grade: "Grade 4B",
    status: "ACTIVE" as const,
    time: "Yesterday",
  },
  {
    name: "Akosua Darko",
    action: "Suspended",
    grade: "Grade 6A",
    status: "SUSPENDED" as const,
    time: "Yesterday",
  },
];

export default function AdminDashboard() {
  return (
    <>
      {/* Top bar */}
      <header className="flex items-center justify-between px-6 py-4 border-b border-border bg-card shrink-0">
        <div>
          <h1 className="text-lg font-semibold">Dashboard</h1>
          <p className="text-xs text-muted-foreground">
            Friday, 23 May 2026 · Term 2
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
        {/* Stat cards */}
        <div className="grid grid-cols-4 gap-4">
          {stats.map(({ label, value, change, positive, icon: Icon, color }) => (
            <div
              key={label}
              className="rounded-xl border border-border bg-card p-4 flex flex-col gap-3"
            >
              <div className="flex items-center justify-between">
                <p className="text-sm text-muted-foreground font-medium">
                  {label}
                </p>
                <span
                  className={`size-8 rounded-lg flex items-center justify-center ${color}`}
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
          ))}
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
                {recentActivity.map(({ name, action, grade, status, time }) => (
                  <tr
                    key={name}
                    className="border-b border-border last:border-0 hover:bg-muted/40 transition-colors"
                  >
                    <td className="px-5 py-3 font-medium">{name}</td>
                    <td className="px-5 py-3 text-muted-foreground">{action}</td>
                    <td className="px-5 py-3 text-muted-foreground">{grade}</td>
                    <td className="px-5 py-3">
                      <StatusBadge status={status} />
                    </td>
                    <td className="px-5 py-3 text-right text-muted-foreground text-xs">
                      {time}
                    </td>
                  </tr>
                ))}
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
                { label: "Add teacher", icon: Users },
                { label: "Create class", icon: BookOpen },
                { label: "Generate report", icon: FileText },
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
    </>
  );
}

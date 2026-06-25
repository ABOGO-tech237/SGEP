import { NextResponse } from "next/server";

import { ApiError, proxyFetch } from "@/lib/server/proxy-fetch";
import type {
  AdminDashboardResponse,
  AdminDashboardStat,
  AdminUserDashboardResponse,
} from "@/lib/types/admin";

function mapAccountStatus(status: string): "ACTIVE" | "SUSPENDED" | "PENDING" {
  if (status === "active") return "ACTIVE";
  if (status === "suspended") return "SUSPENDED";
  return "PENDING";
}

function formatRole(role: string): string {
  const labels: Record<string, string> = {
    superadmin: "Superadmin",
    comptable: "Accountant",
    parent: "Parent",
  };
  return labels[role] ?? role;
}

function mapDashboardResponse(payload: AdminUserDashboardResponse): AdminDashboardResponse {
  const stats: AdminDashboardStat[] = [
    {
      label: "Total Users",
      value: String(payload.total_users),
      change: `${payload.active_users} active accounts`,
      positive: null,
    },
    {
      label: "Active Users",
      value: String(payload.active_users),
      change: `${payload.suspended_users} suspended`,
      positive: payload.active_users > 0,
    },
    {
      label: "Superadmins",
      value: String(payload.superadmins),
      change: `${payload.comptables} accountants`,
      positive: null,
    },
    {
      label: "Parents",
      value: String(payload.parents),
      change: `${payload.total_users} total accounts`,
      positive: null,
    },
  ];

  return {
    generated_at: new Date().toISOString(),
    stats,
    recent_users: payload.recent_users,
    recent_activity: payload.recent_users.map((user) => ({
      id: user.id,
      name: user.name || user.email,
      action: user.email,
      grade: formatRole(user.role),
      status: mapAccountStatus(user.account_status),
      time: user.created_at,
    })),
  };
}

export async function GET(): Promise<Response> {
  try {
    const response = await proxyFetch("/admin/dashboard/");

    if (!response.ok) {
      throw new Error(`Unable to load admin dashboard (${response.status})`);
    }

    const payload = (await response.json()) as AdminUserDashboardResponse;
    const dashboard = mapDashboardResponse(payload);
    return NextResponse.json(dashboard, {
      headers: {
        "Cache-Control": "no-store",
      },
    });
  } catch (error) {
    if (error instanceof ApiError) {
      return NextResponse.json({ error: error.message }, { status: error.status });
    }

    return NextResponse.json(
      { error: "Service unavailable." },
      { status: 503 },
    );
  }
}

import { proxyFetch } from "@/lib/server/proxy-fetch";
import type { AdminDashboardData } from "@/lib/types/admin";

async function fetchDashboard(path: string): Promise<AdminDashboardData | null> {
  const response = await proxyFetch(path);
  if (response.status === 404) {
    return null;
  }
  if (!response.ok) {
    throw new Error(`Failed to load admin dashboard (${response.status}).`);
  }
  return (await response.json()) as AdminDashboardData;
}

export async function getAdminDashboard(): Promise<AdminDashboardData> {
  const primary = await fetchDashboard("/admin/dashboard/");
  if (primary) {
    return primary;
  }

  const fallback = await fetchDashboard("/api/v1/admin/dashboard/");
  if (fallback) {
    return fallback;
  }

  throw new Error("Admin dashboard endpoint not found.");
}
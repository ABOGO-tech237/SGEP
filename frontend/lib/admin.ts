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
  const contentType = response.headers.get("content-type") ?? "";
  if (!contentType.includes("application/json")) {
    throw new Error(`Expected JSON but got ${contentType || "unknown"}`);
  }
  return (await response.json()) as AdminDashboardData;
}

export async function getAdminDashboard(): Promise<AdminDashboardData> {
  // Prefer the API namespace to avoid colliding with Django's admin HTML pages.
  const primary = await fetchDashboard("/api/v1/admin/dashboard/");
  if (primary) return primary;

  const fallback = await fetchDashboard("/admin/dashboard/");
  if (fallback) return fallback;

  throw new Error("Admin dashboard endpoint not found.");
}
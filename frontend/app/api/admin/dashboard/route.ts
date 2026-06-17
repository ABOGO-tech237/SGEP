import { NextResponse } from "next/server";

import { ApiError, proxyFetch } from "@/lib/server/proxy-fetch";
import type { AdminDashboardResponse } from "@/lib/types/admin";

export async function GET(): Promise<Response> {
  try {
    const response = await proxyFetch("/admin/dashboard/");

    if (!response.ok) {
      throw new Error(`Unable to load admin dashboard (${response.status})`);
    }

    const dashboard = (await response.json()) as AdminDashboardResponse;
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

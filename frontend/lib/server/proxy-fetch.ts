import { cookies } from "next/headers";
import { SESSION_COOKIE } from "@/lib/auth/constants";

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export async function proxyFetch(
  path: string,
  init?: RequestInit,
): Promise<Response> {
  const apiUrl = process.env.DJANGO_API_URL;
  if (!apiUrl) throw new Error("DJANGO_API_URL environment variable is not set");

  const cookieStore = await cookies();
  const token = cookieStore.get(SESSION_COOKIE)?.value;
  if (!token) throw new ApiError(401, "No session");

  const response = await fetch(`${apiUrl}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers as Record<string, string> | undefined),
      Authorization: `Bearer ${token}`,
    },
    cache: "no-store",
  });

  if (response.status === 401) {
    throw new ApiError(401, "Session expired");
  }

  return response;
}

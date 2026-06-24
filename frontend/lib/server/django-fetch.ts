import { cookies } from "next/headers";
import { DJANGO_TOKEN_COOKIE } from "@/lib/auth/constants";

export class DjangoApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = "DjangoApiError";
  }
}

export async function djangoFetch(
  path: string,
  init?: RequestInit,
): Promise<Response> {
  const apiUrl = process.env.DJANGO_API_URL;
  if (!apiUrl)
    throw new Error("DJANGO_API_URL environment variable is not set");

  const cookieStore = await cookies();
  const token = cookieStore.get(DJANGO_TOKEN_COOKIE)?.value;
  if (!token) throw new DjangoApiError(503, "Backend session not ready — please wait a moment and refresh the page.");

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
    throw new DjangoApiError(401, "Session expired");
  }

  return response;
}

import { cookies } from "next/headers";
import {
  DJANGO_ACCESS_COOKIE,
  DJANGO_REFRESH_COOKIE,
} from "@/lib/auth/constants";
import { refreshDjangoAccessToken } from "@/lib/server/django-auth";

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

function joinApiPath(apiUrl: string, path: string): string {
  const base = apiUrl.endsWith("/") ? apiUrl : `${apiUrl}/`;
  const suffix = path.startsWith("/") ? path.slice(1) : path;
  return `${base}${suffix}`;
}

async function getDjangoAccessToken(
  cookieStore: Awaited<ReturnType<typeof cookies>>,
  isProd: boolean,
): Promise<string | null> {
  const accessToken = cookieStore.get(DJANGO_ACCESS_COOKIE)?.value;
  if (accessToken) {
    return accessToken;
  }

  const refreshToken = cookieStore.get(DJANGO_REFRESH_COOKIE)?.value;
  if (!refreshToken) {
    return null;
  }

  const refreshed = await refreshDjangoAccessToken(refreshToken);
  if (!refreshed) {
    return null;
  }

  cookieStore.set(DJANGO_ACCESS_COOKIE, refreshed, {
    httpOnly: true,
    secure: isProd,
    sameSite: "strict",
    maxAge: 30 * 60,
    path: "/",
  });

  return refreshed;
}

export async function proxyFetch(
  path: string,
  init?: RequestInit,
): Promise<Response> {
  const apiUrl = process.env.DJANGO_API_URL;
  if (!apiUrl) throw new Error("DJANGO_API_URL environment variable is not set");

  const cookieStore = await cookies();
  const isProd = process.env.NODE_ENV === "production";
  let token = await getDjangoAccessToken(cookieStore, isProd);
  if (!token) throw new ApiError(401, "No session");

  const requestInit: RequestInit = {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers as Record<string, string> | undefined),
      Authorization: `Bearer ${token}`,
    },
    cache: "no-store",
  };

  let response = await fetch(joinApiPath(apiUrl, path), requestInit);

  if (response.status === 401) {
    const refreshToken = cookieStore.get(DJANGO_REFRESH_COOKIE)?.value;
    const refreshed = refreshToken
      ? await refreshDjangoAccessToken(refreshToken)
      : null;

    if (refreshed) {
      cookieStore.set(DJANGO_ACCESS_COOKIE, refreshed, {
        httpOnly: true,
        secure: isProd,
        sameSite: "strict",
        maxAge: 30 * 60,
        path: "/",
      });

      token = refreshed;
      response = await fetch(joinApiPath(apiUrl, path), {
        ...requestInit,
        headers: {
          ...(requestInit.headers as Record<string, string>),
          Authorization: `Bearer ${token}`,
        },
      });
    }
  }

  if (response.status === 401) {
    throw new ApiError(401, "Session expired");
  }

  return response;
}

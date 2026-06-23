import { headers } from "next/headers";

export async function serverApiFetch<T>(
  apiPath: string,
  init?: RequestInit,
): Promise<T | null> {
  const requestHeaders = await headers();
  const host = requestHeaders.get("host");
  if (!host) return null;

  const protocol = requestHeaders.get("x-forwarded-proto") ?? "http";
  const response = await fetch(new URL(apiPath, `${protocol}://${host}`), {
    cache: "no-store",
    ...init,
    headers: {
      cookie: requestHeaders.get("cookie") ?? "",
      ...(init?.headers as Record<string, string> | undefined),
    },
  });

  if (!response.ok) return null;
  return (await response.json()) as T;
}

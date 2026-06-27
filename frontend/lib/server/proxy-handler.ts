import { NextResponse } from "next/server";

import { ApiError, proxyFetch } from "@/lib/server/proxy-fetch";

export async function proxyJsonResponse(
  path: string,
  init?: RequestInit,
): Promise<Response> {
  try {
    const response = await proxyFetch(path, init);
    const text = await response.text();

    if (response.status === 204) {
      return new Response(null, { status: 204 });
    }

    let body: unknown;
    try {
      body = text ? JSON.parse(text) : null;
    } catch {
      console.error("[proxyJsonResponse] non-JSON from backend:", text.slice(0, 500));
      return NextResponse.json(
        { error: "The backend returned an unexpected response." },
        { status: 502 },
      );
    }
    return NextResponse.json(body, { status: response.status });
  } catch (error) {
    if (error instanceof ApiError) {
      return NextResponse.json({ error: error.message }, { status: error.status });
    }

    return NextResponse.json({ error: "Service unavailable." }, { status: 503 });
  }
}

export async function proxyBinaryResponse(
  path: string,
  init?: RequestInit,
): Promise<Response> {
  try {
    const response = await proxyFetch(path, init);
    if (!response.ok) {
      const text = await response.text();
      let body: unknown = { error: "Download failed." };
      try {
        body = text ? JSON.parse(text) : body;
      } catch {
        body = { error: text || "Download failed." };
      }
      return NextResponse.json(body, { status: response.status });
    }

    const buffer = await response.arrayBuffer();
    const headers = new Headers();
    const contentType = response.headers.get("content-type");
    const disposition = response.headers.get("content-disposition");
    if (contentType) headers.set("Content-Type", contentType);
    if (disposition) headers.set("Content-Disposition", disposition);

    return new Response(buffer, { status: 200, headers });
  } catch (error) {
    if (error instanceof ApiError) {
      return NextResponse.json({ error: error.message }, { status: error.status });
    }

    return NextResponse.json({ error: "Service unavailable." }, { status: 503 });
  }
}

export function djangoPathWithSearch(path: string, request: Request): string {
  const url = new URL(request.url);
  const search = url.search;
  if (!search) return path;
  return `${path}${search.startsWith("?") ? search : `?${search}`}`;
}

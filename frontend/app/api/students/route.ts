import { type NextRequest } from "next/server";
import { djangoFetch, DjangoApiError } from "@/lib/server/django-fetch";

export async function GET(request: NextRequest): Promise<Response> {
  try {
    const query = request.nextUrl.searchParams.toString();
    const res = await djangoFetch(
      `/api/v1/students/${query ? `?${query}` : ""}`,
    );
    const data: unknown = await res.json();
    return Response.json(data, { status: res.status });
  } catch (err) {
    if (err instanceof DjangoApiError) {
      return Response.json({ error: err.message }, { status: err.status });
    }
    return Response.json({ error: "Internal error" }, { status: 500 });
  }
}

export async function POST(request: NextRequest): Promise<Response> {
  try {
    const body: unknown = await request.json();
    const res = await djangoFetch("/api/v1/students/", {
      method: "POST",
      body: JSON.stringify(body),
    });
    const data: unknown = await res.json();
    return Response.json(data, { status: res.status });
  } catch (err) {
    if (err instanceof DjangoApiError) {
      return Response.json({ error: err.message }, { status: err.status });
    }
    return Response.json({ error: "Internal error" }, { status: 500 });
  }
}

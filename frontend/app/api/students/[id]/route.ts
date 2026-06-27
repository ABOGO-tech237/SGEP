import { type NextRequest } from "next/server";
import { djangoFetch, DjangoApiError } from "@/lib/server/django-fetch";

type Params = { params: Promise<{ id: string }> };

async function readBody(res: Response): Promise<unknown> {
  const text = await res.text();
  if (!text) return null;
  try { return JSON.parse(text); } catch { return null; }
}

export async function GET(_request: NextRequest, { params }: Params): Promise<Response> {
  try {
    const { id } = await params;
    const res = await djangoFetch(`/students/${id}/`);
    const data = await readBody(res);
    if (data === null) return new Response(null, { status: res.status });
    return Response.json(data, { status: res.status });
  } catch (err) {
    if (err instanceof DjangoApiError) {
      return Response.json({ error: err.message }, { status: err.status });
    }
    return Response.json({ error: "Internal error" }, { status: 500 });
  }
}

export async function PATCH(request: NextRequest, { params }: Params): Promise<Response> {
  try {
    const { id } = await params;
    const body: unknown = await request.json();
    const res = await djangoFetch(`/students/${id}/`, {
      method: "PATCH",
      body: JSON.stringify(body),
    });
    const data = await readBody(res);
    if (data === null) return new Response(null, { status: res.status });
    return Response.json(data, { status: res.status });
  } catch (err) {
    if (err instanceof DjangoApiError) {
      return Response.json({ error: err.message }, { status: err.status });
    }
    return Response.json({ error: "Internal error" }, { status: 500 });
  }
}

export async function DELETE(_request: NextRequest, { params }: Params): Promise<Response> {
  try {
    const { id } = await params;
    const res = await djangoFetch(`/students/${id}/`, {
      method: "DELETE",
    });
    const data = await readBody(res);
    if (data === null) return new Response(null, { status: res.status });
    return Response.json(data, { status: res.status });
  } catch (err) {
    if (err instanceof DjangoApiError) {
      return Response.json({ error: err.message }, { status: err.status });
    }
    return Response.json({ error: "Internal error" }, { status: 500 });
  }
}

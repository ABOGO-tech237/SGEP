import { proxyJsonResponse } from "@/lib/server/proxy-handler";

interface RouteContext {
  params: Promise<{ id: string }>;
}

export async function GET(
  _request: Request,
  context: RouteContext,
): Promise<Response> {
  const { id } = await context.params;
  return proxyJsonResponse(`/students/${id}/`);
}

export async function PATCH(
  request: Request,
  context: RouteContext,
): Promise<Response> {
  const { id } = await context.params;
  const body = await request.text();
  return proxyJsonResponse(`/students/${id}/`, {
    method: "PATCH",
    body,
  });
}

export async function DELETE(
  _request: Request,
  context: RouteContext,
): Promise<Response> {
  const { id } = await context.params;
  return proxyJsonResponse(`/students/${id}/`, { method: "DELETE" });
}

import { proxyJsonResponse } from "@/lib/server/proxy-handler";

interface RouteContext {
  params: Promise<{ id: string }>;
}

export async function GET(
  _request: Request,
  context: RouteContext,
): Promise<Response> {
  const { id } = await context.params;
  return proxyJsonResponse(`/classes/${id}/`);
}

export async function PATCH(
  request: Request,
  context: RouteContext,
): Promise<Response> {
  const { id } = await context.params;
  const body = await request.text();
  return proxyJsonResponse(`/classes/${id}/`, {
    method: "PATCH",
    body,
  });
}

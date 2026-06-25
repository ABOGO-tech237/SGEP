import { proxyJsonResponse } from "@/lib/server/proxy-handler";

interface RouteContext {
  params: Promise<{ id: string }>;
}

export async function GET(
  _request: Request,
  context: RouteContext,
): Promise<Response> {
  const { id } = await context.params;
  return proxyJsonResponse(`/students/${id}/history/`);
}

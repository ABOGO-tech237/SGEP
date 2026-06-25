import { proxyJsonResponse } from "@/lib/server/proxy-handler";

interface RouteContext {
  params: Promise<{ id: string }>;
}

export async function POST(
  request: Request,
  context: RouteContext,
): Promise<Response> {
  const { id } = await context.params;
  const body = await request.text();
  return proxyJsonResponse(`/students/${id}/promote/`, {
    method: "POST",
    body,
  });
}

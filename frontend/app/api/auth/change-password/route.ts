import { proxyJsonResponse } from "@/lib/server/proxy-handler";

export async function POST(request: Request): Promise<Response> {
  const body = await request.text();
  return proxyJsonResponse("/auth/change-password/", {
    method: "POST",
    body,
  });
}

import { proxyJsonResponse } from "@/lib/server/proxy-handler";

export async function POST(request: Request): Promise<Response> {
  const body = await request.text();
  return proxyJsonResponse("/report-cards/generate/", {
    method: "POST",
    body,
  });
}

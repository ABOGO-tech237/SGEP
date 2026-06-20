import { proxyJsonResponse } from "@/lib/server/proxy-handler";

export async function GET(): Promise<Response> {
  return proxyJsonResponse("/schools/");
}

export async function POST(request: Request): Promise<Response> {
  const body = await request.text();
  return proxyJsonResponse("/schools/", {
    method: "POST",
    body,
  });
}

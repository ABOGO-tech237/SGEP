import {
  djangoPathWithSearch,
  proxyJsonResponse,
} from "@/lib/server/proxy-handler";

export async function GET(request: Request): Promise<Response> {
  return proxyJsonResponse(djangoPathWithSearch("/subjects/", request));
}

export async function POST(request: Request): Promise<Response> {
  const body = await request.text();
  return proxyJsonResponse("/subjects/", {
    method: "POST",
    body,
  });
}

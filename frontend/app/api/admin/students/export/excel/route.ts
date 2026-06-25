import {
  djangoPathWithSearch,
  proxyJsonResponse,
} from "@/lib/server/proxy-handler";

export async function GET(request: Request): Promise<Response> {
  return proxyJsonResponse(djangoPathWithSearch("/students/export/excel/", request));
}

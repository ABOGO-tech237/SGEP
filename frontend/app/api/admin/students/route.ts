import {
  djangoPathWithSearch,
  proxyJsonResponse,
} from "@/lib/server/proxy-handler";
import { CreateStudentSchema } from "@/lib/types/students";

export async function GET(request: Request): Promise<Response> {
  return proxyJsonResponse(djangoPathWithSearch("/students/", request));
}

export async function POST(request: Request): Promise<Response> {
  const raw = await request.text();
  let body: unknown;
  try {
    body = raw ? JSON.parse(raw) : {};
  } catch {
    return Response.json({ error: "Invalid JSON body." }, { status: 400 });
  }

  const parsed = CreateStudentSchema.safeParse(body);
  if (!parsed.success) {
    const fieldErrors = parsed.error.flatten().fieldErrors;
    const firstError = Object.values(fieldErrors).flat()[0];
    return Response.json(
      { error: typeof firstError === "string" ? firstError : "Invalid student payload." },
      { status: 400 },
    );
  }

  return proxyJsonResponse("/students/", {
    method: "POST",
    body: JSON.stringify(parsed.data),
  });
}

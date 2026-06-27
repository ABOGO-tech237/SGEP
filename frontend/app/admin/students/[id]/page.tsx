import { notFound } from "next/navigation";
import { djangoFetch, DjangoApiError } from "@/lib/server/django-fetch";
import { StudentDetailSchema, type StudentDetail } from "@/lib/types/students";
import { StudentDetailClient } from "./StudentDetailClient";

type Props = { params: Promise<{ id: string }> };

async function fetchStudent(id: string): Promise<StudentDetail | null> {
  try {
    const res = await djangoFetch(`/students/${id}/`);
    if (!res.ok) return null;
    const raw: unknown = await res.json();
    return StudentDetailSchema.parse(raw);
  } catch (err) {
    if (err instanceof DjangoApiError && err.status === 404) return null;
    throw err;
  }
}

export default async function StudentDetailPage({ params }: Props) {
  const { id } = await params;
  const student = await fetchStudent(id);

  if (!student) notFound();

  return <StudentDetailClient student={student} />;
}

import { GraduationCap, FileText } from "lucide-react";
import { djangoFetch, DjangoApiError } from "@/lib/server/django-fetch";
import type { StudentsListResponse } from "@/lib/types/students";
import { StudentsTable } from "./StudentsTable";
import { EnrolStudentButton } from "./EnrolStudentButton";

async function fetchStudents(): Promise<StudentsListResponse> {
  const res = await djangoFetch("/api/v1/students/?page_size=100");
  if (!res.ok) {
    throw new DjangoApiError(res.status, "Failed to load students");
  }
  return res.json() as Promise<StudentsListResponse>;
}

export default async function StudentsPage() {
  let data: StudentsListResponse | null = null;
  let fetchError: string | null = null;

  try {
    data = await fetchStudents();
  } catch (err) {
    fetchError =
      err instanceof DjangoApiError
        ? err.message
        : "Could not load students.";
  }

  const students = data?.items ?? [];
  const total = data?.total ?? 0;

  return (
    <>
      {/* Top bar */}
      <header className="flex items-center justify-between px-6 py-4 border-b border-border bg-card shrink-0">
        <div>
          <h1 className="text-lg font-semibold">Students</h1>
          <p className="text-xs text-muted-foreground">
            {total} student{total !== 1 ? "s" : ""} enrolled
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button className="inline-flex items-center gap-1.5 rounded-md border border-input bg-background px-3 py-1.5 text-sm font-medium transition hover:bg-muted">
            <FileText className="size-3.5" />
            Export
          </button>
          <EnrolStudentButton />
          <div className="size-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xs font-semibold">
            AD
          </div>
        </div>
      </header>

      {/* Body */}
      <main className="flex-1 overflow-y-auto px-6 py-6">
        {fetchError ? (
          <div
            role="alert"
            className="rounded-xl border border-destructive/40 bg-destructive/10 px-5 py-4 text-sm text-destructive"
          >
            {fetchError}
          </div>
        ) : students.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-center gap-3">
            <GraduationCap className="size-10 text-muted-foreground/40" />
            <p className="text-sm text-muted-foreground">No students enrolled yet.</p>
            <EnrolStudentButton />
          </div>
        ) : (
          <StudentsTable students={students} />
        )}
      </main>
    </>
  );
}

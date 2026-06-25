"use client";

import { useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { AdminShell } from "@/components/admin/AdminShell";
import { Button } from "@/components/ui/button";
import { FormField } from "@/components/ui/FormField";
import { StatusBadge } from "@/components/ui/StatusBadge";
import type { ClassRecord } from "@/lib/types/classes";
import {
  StudentCreateSchema,
  type StudentCreateValues,
  type StudentDetail,
} from "@/lib/types/students";

async function fetchStudent(id: string): Promise<StudentDetail> {
  const response = await fetch(`/api/admin/students/${id}`);
  if (!response.ok) throw new Error("Unable to load student.");
  return (await response.json()) as StudentDetail;
}

async function fetchClasses(): Promise<ClassRecord[]> {
  const response = await fetch("/api/admin/classes");
  if (!response.ok) throw new Error("Unable to load classes.");
  return (await response.json()) as ClassRecord[];
}

export default function StudentDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const queryClient = useQueryClient();
  const studentId = params.id;

  const studentQuery = useQuery({
    queryKey: ["admin", "students", studentId],
    queryFn: () => fetchStudent(studentId),
  });
  const classesQuery = useQuery({ queryKey: ["admin", "classes"], queryFn: fetchClasses });

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<StudentCreateValues>({
    resolver: zodResolver(StudentCreateSchema),
  });

  const student = studentQuery.data;

  useEffect(() => {
    if (!student) return;
    reset({
      first_name: student.first_name,
      last_name: student.last_name,
      matricule: student.matricule,
      birth_date: student.birth_date,
      birth_place: student.birth_place,
      gender: student.gender,
      class_id: student.class_id ?? "",
      academic_year_id: student.academic_year_id ?? "",
      is_active: student.is_active,
    });
  }, [student, reset]);

  const updateStudent = useMutation({
    mutationFn: async (values: StudentCreateValues) => {
      const response = await fetch(`/api/admin/students/${studentId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(values),
      });
      const payload = (await response.json()) as { error?: string };
      if (!response.ok) throw new Error(payload.error ?? "Unable to update student.");
      return payload;
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["admin", "students", studentId] });
    },
  });

  const deleteStudent = useMutation({
    mutationFn: async () => {
      const response = await fetch(`/api/admin/students/${studentId}`, { method: "DELETE" });
      if (!response.ok) {
        const payload = (await response.json()) as { error?: string };
        throw new Error(payload.error ?? "Unable to delete student.");
      }
    },
    onSuccess: () => router.push("/admin/students"),
  });

  const promoteStudent = useMutation({
    mutationFn: async (targetClassId: string) => {
      const response = await fetch(`/api/admin/students/${studentId}/promote`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ target_class_id: targetClassId }),
      });
      const payload = (await response.json()) as { error?: string };
      if (!response.ok) throw new Error(payload.error ?? "Unable to promote student.");
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["admin", "students", studentId] });
    },
  });

  return (
    <AdminShell
      title={student ? `${student.first_name} ${student.last_name}` : "Student"}
      description={student?.matricule}
      actions={
        student ? (
          <StatusBadge status={student.is_active === false ? "SUSPENDED" : "ACTIVE"} />
        ) : null
      }
    >
      {studentQuery.isLoading ? (
        <p className="text-sm text-muted-foreground">Loading student…</p>
      ) : studentQuery.error ? (
        <p className="text-sm text-destructive">Unable to load student.</p>
      ) : (
        <div className="grid gap-6 lg:grid-cols-[2fr_1fr]">
          <form
            onSubmit={handleSubmit((values) => updateStudent.mutate(values))}
            className="space-y-4 rounded-xl border border-border bg-card p-6"
            noValidate
          >
            <h2 className="text-sm font-semibold">Profile</h2>
            <div className="grid grid-cols-2 gap-4">
              <FormField label="First name" name="first_name" error={errors.first_name} required>
                <input
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  {...register("first_name")}
                />
              </FormField>
              <FormField label="Last name" name="last_name" error={errors.last_name} required>
                <input
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  {...register("last_name")}
                />
              </FormField>
              <FormField label="Matricule" name="matricule" error={errors.matricule} required>
                <input
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  {...register("matricule")}
                />
              </FormField>
              <FormField label="Class" name="class_id" error={errors.class_id} required>
                <select
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  {...register("class_id")}
                >
                  {(classesQuery.data ?? []).map((item) => (
                    <option key={item.id} value={item.id}>
                      {item.name}
                    </option>
                  ))}
                </select>
              </FormField>
            </div>
            <div className="flex gap-3">
              <Button type="submit" disabled={updateStudent.isPending}>
                {updateStudent.isPending ? "Saving…" : "Save changes"}
              </Button>
              <Button
                type="button"
                variant="destructive"
                disabled={deleteStudent.isPending}
                onClick={() => {
                  if (window.confirm("Archive this student record?")) {
                    deleteStudent.mutate();
                  }
                }}
              >
                Archive
              </Button>
            </div>
          </form>

          <div className="space-y-4">
            <div className="rounded-xl border border-border bg-card p-5 space-y-3">
              <h2 className="text-sm font-semibold">Promote</h2>
              <p className="text-xs text-muted-foreground">
                Move the student to another class for the next level.
              </p>
              <select
                id="promote-class"
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                defaultValue=""
              >
                <option value="" disabled>
                  Select target class
                </option>
                {(classesQuery.data ?? []).map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.name}
                  </option>
                ))}
              </select>
              <Button
                type="button"
                variant="outline"
                className="w-full"
                disabled={promoteStudent.isPending}
                onClick={() => {
                  const select = document.getElementById("promote-class") as HTMLSelectElement;
                  if (select.value) promoteStudent.mutate(select.value);
                }}
              >
                Promote student
              </Button>
            </div>

            {student?.medical ? (
              <div className="rounded-xl border border-border bg-card p-5 space-y-2">
                <h2 className="text-sm font-semibold">Medical notes</h2>
                <pre className="text-xs text-muted-foreground whitespace-pre-wrap">
                  {JSON.stringify(student.medical, null, 2)}
                </pre>
              </div>
            ) : null}
          </div>
        </div>
      )}
    </AdminShell>
  );
}

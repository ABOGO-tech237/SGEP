"use client";

import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery } from "@tanstack/react-query";

import { AdminShell } from "@/components/admin/AdminShell";
import { Button } from "@/components/ui/button";
import { FormField } from "@/components/ui/FormField";
import type { AcademicYearRecord } from "@/lib/types/core";
import type { ClassRecord } from "@/lib/types/classes";
import {
  CreateStudentSchema,
  type CreateStudentFormValues,
} from "@/lib/types/students";

async function fetchClasses(): Promise<ClassRecord[]> {
  const response = await fetch("/api/admin/classes");
  if (!response.ok) throw new Error("Unable to load classes.");
  return (await response.json()) as ClassRecord[];
}

async function fetchAcademicYears(): Promise<AcademicYearRecord[]> {
  const response = await fetch("/api/admin/academic-years");
  if (!response.ok) throw new Error("Unable to load academic years.");
  return (await response.json()) as AcademicYearRecord[];
}

export default function NewStudentPage() {
  const router = useRouter();
  const classesQuery = useQuery({ queryKey: ["admin", "classes"], queryFn: fetchClasses });
  const yearsQuery = useQuery({
    queryKey: ["admin", "academic-years"],
    queryFn: fetchAcademicYears,
  });

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<CreateStudentFormValues>({
    resolver: zodResolver(CreateStudentSchema),
    defaultValues: { is_active: true, gender: "M" },
  });

  const createStudent = useMutation({
    mutationFn: async (values: CreateStudentFormValues) => {
      const response = await fetch("/api/admin/students", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(values),
      });
      const payload = (await response.json()) as { id?: string; error?: string };
      if (!response.ok) {
        throw new Error(payload.error ?? "Unable to create student.");
      }
      return payload;
    },
    onSuccess: (payload) => {
      if (payload.id) {
        router.push(`/admin/students/${payload.id}`);
      } else {
        router.push("/admin/students");
      }
    },
  });

  return (
    <AdminShell
      title="Enrol student"
      description="Register a new student — the matricule is assigned automatically"
    >
      <form
        onSubmit={handleSubmit((values) => createStudent.mutate(values))}
        className="max-w-2xl space-y-4 rounded-xl border border-border bg-card p-6"
        noValidate
      >
        {createStudent.error ? (
          <p className="text-sm text-destructive" role="alert">
            {createStudent.error instanceof Error
              ? createStudent.error.message
              : "Unable to create student."}
          </p>
        ) : null}

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
          <FormField label="Gender" name="gender" error={errors.gender} required>
            <select
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              {...register("gender")}
            >
              <option value="M">Male</option>
              <option value="F">Female</option>
            </select>
          </FormField>
          <FormField label="Birth date" name="birth_date" error={errors.birth_date} required>
            <input
              type="date"
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              {...register("birth_date")}
            />
          </FormField>
          <FormField label="Birth place" name="birth_place" error={errors.birth_place} required>
            <input
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              {...register("birth_place")}
            />
          </FormField>
          <FormField label="Class" name="class_id" error={errors.class_id} required>
            <select
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              {...register("class_id")}
            >
              <option value="">Select class</option>
              {(classesQuery.data ?? []).map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name}
                </option>
              ))}
            </select>
          </FormField>
          <FormField
            label="Academic year"
            name="academic_year_id"
            error={errors.academic_year_id}
            required
          >
            <select
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              {...register("academic_year_id")}
            >
              <option value="">Select year</option>
              {(yearsQuery.data ?? []).map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name}
                </option>
              ))}
            </select>
          </FormField>
        </div>

        <div className="flex gap-3 pt-2">
          <Button type="submit" disabled={createStudent.isPending}>
            {createStudent.isPending ? "Creating…" : "Create student"}
          </Button>
          <Button type="button" variant="outline" onClick={() => router.back()}>
            Cancel
          </Button>
        </div>
      </form>
    </AdminShell>
  );
}

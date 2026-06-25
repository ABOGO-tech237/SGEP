"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { X } from "lucide-react";

import { Button } from "@/components/ui/button";
import { FormField } from "@/components/ui/FormField";
import type { AcademicYearRecord } from "@/lib/types/core";
import type { ClassRecord } from "@/lib/types/classes";
import {
  StudentCreateSchema,
  type StudentCreateValues,
} from "@/lib/types/students";

interface EnrolStudentModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const inputClass =
  "w-full rounded-md border border-input bg-background px-3 py-2 text-sm";

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

export function EnrolStudentModal({ open, onOpenChange }: EnrolStudentModalProps) {
  const queryClient = useQueryClient();
  const [serverError, setServerError] = useState<string | null>(null);

  const classesQuery = useQuery({
    queryKey: ["admin", "classes"],
    queryFn: fetchClasses,
    enabled: open,
  });
  const yearsQuery = useQuery({
    queryKey: ["admin", "academic-years"],
    queryFn: fetchAcademicYears,
    enabled: open,
  });

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<StudentCreateValues>({
    resolver: zodResolver(StudentCreateSchema),
    defaultValues: { is_active: true, gender: "M" },
  });

  const createStudent = useMutation({
    mutationFn: async (values: StudentCreateValues) => {
      const response = await fetch("/api/admin/students", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(values),
      });
      const payload = (await response.json()) as { error?: string };
      if (!response.ok) {
        throw new Error(payload.error ?? "Unable to enrol student.");
      }
      return payload;
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["admin", "students"] });
      reset({ is_active: true, gender: "M" });
      setServerError(null);
      onOpenChange(false);
    },
    onError: (error) => {
      setServerError(error instanceof Error ? error.message : "Unable to enrol student.");
    },
  });

  function handleClose() {
    reset({ is_active: true, gender: "M" });
    setServerError(null);
    onOpenChange(false);
  }

  if (!open) return null;

  const busy = isSubmitting || createStudent.isPending;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="enrol-modal-title"
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
    >
      <div className="absolute inset-0 bg-black/50" onClick={handleClose} aria-hidden />
      <div className="relative z-10 flex max-h-[90vh] w-full max-w-2xl flex-col overflow-hidden rounded-xl border border-border bg-card shadow-xl">
        <div className="flex shrink-0 items-center justify-between border-b border-border px-6 py-4">
          <div>
            <h2 id="enrol-modal-title" className="text-base font-semibold">
              Enrol new student
            </h2>
            <p className="mt-0.5 text-xs text-muted-foreground">
              Enter enrollment details — the matricule is assigned automatically
            </p>
          </div>
          <button
            type="button"
            aria-label="Close"
            onClick={handleClose}
            className="rounded-lg p-1.5 text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
          >
            <X className="size-4" />
          </button>
        </div>

        <form
          onSubmit={handleSubmit((values) => createStudent.mutate(values))}
          noValidate
          className="flex flex-1 flex-col overflow-hidden"
        >
          <div className="flex-1 overflow-y-auto px-6 py-5">
            {serverError ? (
              <div
                role="alert"
                className="mb-4 rounded-lg border border-destructive/50 bg-destructive/10 px-4 py-3 text-sm text-destructive"
              >
                {serverError}
              </div>
            ) : null}

            <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              Personal information
            </p>
            <div className="mb-6 grid grid-cols-2 gap-4">
              <FormField label="First name" name="first_name" error={errors.first_name} required>
                <input className={inputClass} autoComplete="off" {...register("first_name")} />
              </FormField>
              <FormField label="Last name" name="last_name" error={errors.last_name} required>
                <input className={inputClass} autoComplete="off" {...register("last_name")} />
              </FormField>
              <FormField label="Gender" name="gender" error={errors.gender} required>
                <select className={inputClass} {...register("gender")}>
                  <option value="M">Male</option>
                  <option value="F">Female</option>
                </select>
              </FormField>
              <FormField label="Birth date" name="birth_date" error={errors.birth_date} required>
                <input type="date" className={inputClass} {...register("birth_date")} />
              </FormField>
              <FormField label="Birth place" name="birth_place" error={errors.birth_place} required>
                <input className={inputClass} autoComplete="off" {...register("birth_place")} />
              </FormField>
            </div>

            <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              Enrollment
            </p>
            <div className="grid grid-cols-2 gap-4">
              <FormField label="Class" name="class_id" error={errors.class_id} required>
                <select className={inputClass} {...register("class_id")}>
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
                <select className={inputClass} {...register("academic_year_id")}>
                  <option value="">Select year</option>
                  {(yearsQuery.data ?? []).map((item) => (
                    <option key={item.id} value={item.id}>
                      {item.name}
                    </option>
                  ))}
                </select>
              </FormField>
            </div>
          </div>

          <div className="flex shrink-0 justify-end gap-3 border-t border-border px-6 py-4">
            <Button type="button" variant="outline" disabled={busy} onClick={handleClose}>
              Cancel
            </Button>
            <Button type="submit" disabled={busy}>
              {busy ? "Saving…" : "Enrol student"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}

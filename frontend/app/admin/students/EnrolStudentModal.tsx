"use client";

import { useState, useTransition } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { X } from "lucide-react";
import { FormField } from "@/components/ui/FormField";
import {
  CreateStudentSchema,
  type CreateStudentFormValues,
} from "@/lib/types/students";

interface EnrolStudentModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const inputClass =
  "w-full rounded-md border border-input bg-background px-3 py-2 text-sm outline-none ring-offset-background transition focus-visible:ring-2 focus-visible:ring-ring aria-invalid:border-destructive";

export function EnrolStudentModal({ open, onOpenChange }: EnrolStudentModalProps) {
  const router = useRouter();
  const [isPending, startTransition] = useTransition();
  const [serverError, setServerError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<CreateStudentFormValues>({
    resolver: zodResolver(CreateStudentSchema),
  });

  function handleClose() {
    reset();
    setServerError(null);
    onOpenChange(false);
  }

  async function onSubmit(data: CreateStudentFormValues) {
    setServerError(null);

    const res = await fetch("/api/students", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      const detail = (body as { detail?: string; error?: string }).detail ?? (body as { error?: string }).error ?? "Failed to enrol student.";
      setServerError(detail);
      return;
    }

    handleClose();
    startTransition(() => router.refresh());
  }

  if (!open) return null;

  const busy = isSubmitting || isPending;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="enrol-modal-title"
      className="fixed inset-0 z-50 flex items-center justify-center"
    >
      <div
        className="absolute inset-0 bg-black/50"
        onClick={handleClose}
        aria-hidden
      />
      <div className="relative z-10 w-full max-w-lg rounded-xl border border-border bg-card shadow-lg">
        <div className="flex items-center justify-between px-6 py-4 border-b border-border">
          <h2 id="enrol-modal-title" className="text-base font-semibold">
            Enrol new student
          </h2>
          <button
            aria-label="Close"
            onClick={handleClose}
            className="rounded p-1 text-muted-foreground hover:text-foreground"
          >
            <X className="size-4" />
          </button>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} noValidate>
          <div className="px-6 py-5 grid grid-cols-2 gap-4">
            {serverError && (
              <div
                role="alert"
                className="col-span-2 rounded-md border border-destructive/50 bg-destructive/10 px-4 py-3 text-sm text-destructive"
              >
                {serverError}
              </div>
            )}

            <FormField label="First name" name="first_name" error={errors.first_name} required>
              <input className={inputClass} {...register("first_name")} />
            </FormField>

            <FormField label="Last name" name="last_name" error={errors.last_name} required>
              <input className={inputClass} {...register("last_name")} />
            </FormField>

            <FormField label="Matricule" name="matricule" error={errors.matricule} required>
              <input className={inputClass} {...register("matricule")} />
            </FormField>

            <FormField label="Gender" name="gender" error={errors.gender} required>
              <select className={inputClass} {...register("gender")}>
                <option value="">Select…</option>
                <option value="M">Male</option>
                <option value="F">Female</option>
              </select>
            </FormField>

            <FormField
              label="Date of birth"
              name="birth_date"
              error={errors.birth_date}
              required
            >
              <input type="date" className={inputClass} {...register("birth_date")} />
            </FormField>

            <FormField label="Place of birth" name="birth_place" error={errors.birth_place} required>
              <input className={inputClass} {...register("birth_place")} />
            </FormField>

            <FormField
              label="Class ID"
              name="class_id"
              error={errors.class_id}
              required
              description="Appwrite document ID of the class"
            >
              <input className={inputClass} {...register("class_id")} />
            </FormField>

            <FormField
              label="Academic year ID"
              name="academic_year_id"
              error={errors.academic_year_id}
              required
              description="Appwrite document ID of the academic year"
            >
              <input className={inputClass} {...register("academic_year_id")} />
            </FormField>

            <FormField
              label="ID / Extrait number"
              name="id_number"
              error={errors.id_number}
              className="col-span-2"
            >
              <input className={inputClass} {...register("id_number")} />
            </FormField>
          </div>

          <div className="flex justify-end gap-3 px-6 py-4 border-t border-border">
            <button
              type="button"
              onClick={handleClose}
              disabled={busy}
              className="rounded-md border border-input bg-background px-4 py-2 text-sm font-medium transition hover:bg-muted disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={busy}
              className="rounded-md bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground transition hover:bg-primary/90 disabled:opacity-50"
            >
              {busy ? "Saving…" : "Enrol student"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

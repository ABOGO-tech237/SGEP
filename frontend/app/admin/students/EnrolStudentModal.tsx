"use client";

import { useState, useTransition } from "react";
import { useForm, Controller } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { X } from "lucide-react";
import { FormField } from "@/components/ui/FormField";
import { DatePicker } from "@/components/ui/DatePicker";
import {
  StudentCreateSchema,
  type StudentCreateValues,
} from "@/lib/types/students";

interface EnrolStudentModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const inputClass =
  "w-full rounded-md border border-input bg-background px-3 py-2 text-sm outline-none ring-offset-background transition focus-visible:ring-2 focus-visible:ring-ring aria-invalid:border-destructive";

function extractError(body: unknown, fallback: string): string {
  if (typeof body !== "object" || body === null) return fallback;
  const b = body as Record<string, unknown>;
  const candidate = b.detail ?? b.error ?? b.message;
  if (typeof candidate === "string") return candidate;
  return fallback;
}

export function EnrolStudentModal({ open, onOpenChange }: EnrolStudentModalProps) {
  const router = useRouter();
  const [isPending, startTransition] = useTransition();
  const [serverError, setServerError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    reset,
    control,
    formState: { errors, isSubmitting },
  } = useForm<StudentCreateValues>({
    resolver: zodResolver(StudentCreateSchema),
  });

  function handleClose() {
    reset();
    setServerError(null);
    onOpenChange(false);
  }

  async function onSubmit(data: StudentCreateValues) {
    setServerError(null);

    const res = await fetch("/api/students", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    if (!res.ok) {
      const body: unknown = await res.json().catch(() => ({}));
      setServerError(extractError(body, "Failed to enrol student."));
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
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
    >
      <div
        className="absolute inset-0 bg-black/50"
        onClick={handleClose}
        aria-hidden
      />
      <div className="relative z-10 w-full max-w-2xl rounded-xl border border-border bg-card shadow-xl flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-border shrink-0">
          <div>
            <h2 id="enrol-modal-title" className="text-base font-semibold">
              Enrol new student
            </h2>
            <p className="text-xs text-muted-foreground mt-0.5">
              Fill in the student&apos;s information below
            </p>
          </div>
          <button
            aria-label="Close"
            onClick={handleClose}
            className="rounded-lg p-1.5 text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
          >
            <X className="size-4" />
          </button>
        </div>

        {/* Body */}
        <form onSubmit={handleSubmit(onSubmit)} noValidate className="flex flex-col flex-1 overflow-hidden">
          <div className="px-6 py-5 overflow-y-auto flex-1">
            {serverError && (
              <div
                role="alert"
                className="mb-4 rounded-lg border border-destructive/50 bg-destructive/10 px-4 py-3 text-sm text-destructive"
              >
                {serverError}
              </div>
            )}

            {/* Section: Personal */}
            <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-3">
              Personal information
            </p>
            <div className="grid grid-cols-3 gap-4 mb-6">
              <FormField label="First name" name="first_name" error={errors.first_name} required>
                <input className={inputClass} {...register("first_name")} />
              </FormField>

              <FormField label="Last name" name="last_name" error={errors.last_name} required>
                <input className={inputClass} {...register("last_name")} />
              </FormField>

              <FormField label="Gender" name="gender" error={errors.gender} required>
                <select className={inputClass} {...register("gender")}>
                  <option value="">Select…</option>
                  <option value="M">Male</option>
                  <option value="F">Female</option>
                </select>
              </FormField>

              <FormField label="Date of birth" name="birth_date" error={errors.birth_date} required>
                <Controller
                  name="birth_date"
                  control={control}
                  render={({ field }) => (
                    <DatePicker
                      value={field.value}
                      onChange={field.onChange}
                      placeholder="Pick a date"
                    />
                  )}
                />
              </FormField>

              <FormField label="Place of birth" name="birth_place" error={errors.birth_place} required className="col-span-2">
                <input className={inputClass} {...register("birth_place")} />
              </FormField>
            </div>

            {/* Section: Enrollment */}
            <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-3">
              Enrollment
            </p>
            <div className="grid grid-cols-2 gap-4">
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
                <input className={inputClass} placeholder="Optional" {...register("id_number")} />
              </FormField>
            </div>
          </div>

          {/* Footer */}
          <div className="flex justify-end gap-3 px-6 py-4 border-t border-border shrink-0">
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
              className="rounded-md bg-primary px-5 py-2 text-sm font-semibold text-primary-foreground transition hover:bg-primary/90 disabled:opacity-50"
            >
              {busy ? "Saving…" : "Enrol student"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

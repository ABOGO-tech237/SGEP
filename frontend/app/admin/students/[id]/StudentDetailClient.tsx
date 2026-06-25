"use client";

import { useState, useTransition } from "react";
import { useForm, Controller } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { ArrowLeft, Pencil, Trash2, X } from "lucide-react";
import { FormField } from "@/components/ui/FormField";
import { DatePicker } from "@/components/ui/DatePicker";
import { ConfirmDialog } from "@/components/ui/ConfirmDialog";
import {
  StudentCreateSchema,
  type StudentCreateValues,
  type StudentDetail,
} from "@/lib/types/students";

function extractError(body: unknown, fallback: string): string {
  if (typeof body !== "object" || body === null) return fallback;
  const b = body as Record<string, unknown>;
  const candidate = b.detail ?? b.error ?? b.message;
  if (typeof candidate === "string") return candidate;
  return fallback;
}

const inputClass =
  "w-full rounded-md border border-input bg-background px-3 py-2 text-sm outline-none ring-offset-background transition focus-visible:ring-2 focus-visible:ring-ring aria-invalid:border-destructive";

interface Props {
  student: StudentDetail;
}

export function StudentDetailClient({ student }: Props) {
  const router = useRouter();
  const [, startTransition] = useTransition();
  const [editOpen, setEditOpen] = useState(false);
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [serverError, setServerError] = useState<string | null>(null);
  const [deleteError, setDeleteError] = useState<string | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    control,
    formState: { errors, isSubmitting },
  } = useForm<StudentCreateValues>({
    resolver: zodResolver(StudentCreateSchema),
    defaultValues: {
      first_name: student.first_name,
      last_name: student.last_name,
      birth_date: student.birth_date,
      birth_place: student.birth_place,
      gender: student.gender as "M" | "F",
      class_id: student.class_id ?? "",
      academic_year_id: student.academic_year_id ?? "",
      id_number: student.id_number ?? "",
      is_active: student.is_active ?? true,
    },
  });

  function handleEditClose() {
    reset();
    setServerError(null);
    setEditOpen(false);
  }

  async function onSubmit(data: StudentCreateValues) {
    setServerError(null);
    const res = await fetch(`/api/students/${student.id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    if (!res.ok) {
      const body: unknown = await res.json().catch(() => ({}));
      setServerError(extractError(body, "Failed to update student."));
      return;
    }

    handleEditClose();
    startTransition(() => router.refresh());
  }

  async function handleDelete() {
    setIsDeleting(true);
    setDeleteError(null);
    try {
      const res = await fetch(`/api/students/${student.id}`, {
        method: "DELETE",
      });

      if (!res.ok) {
        const body: unknown = await res.json().catch(() => ({}));
        setDeleteError(extractError(body, "Could not delete student. Please try again."));
        return;
      }

      router.replace("/admin/students");
    } finally {
      setIsDeleting(false);
    }
  }

  const busy = isSubmitting;

  return (
    <>
      {/* Header */}
      <header className="flex items-center justify-between px-6 py-4 border-b border-border bg-card shrink-0">
        <div className="flex items-center gap-3">
          <button
            onClick={() => router.back()}
            className="rounded p-1.5 text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
            aria-label="Go back"
          >
            <ArrowLeft className="size-4" />
          </button>
          <div>
            <h1 className="text-lg font-semibold">
              {student.first_name} {student.last_name}
            </h1>
            <p className="text-xs text-muted-foreground">{student.matricule}</p>
          </div>
          <span
            className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${
              student.is_active
                ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-900/20 dark:text-emerald-400"
                : "bg-muted text-muted-foreground"
            }`}
          >
            {student.is_active ? "Active" : "Inactive"}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setEditOpen(true)}
            className="inline-flex items-center gap-1.5 rounded-md border border-input bg-background px-3 py-1.5 text-sm font-medium transition hover:bg-muted"
          >
            <Pencil className="size-3.5" />
            Edit
          </button>
          <button
            onClick={() => setDeleteOpen(true)}
            className="inline-flex items-center gap-1.5 rounded-md border border-destructive/40 bg-destructive/5 px-3 py-1.5 text-sm font-medium text-destructive transition hover:bg-destructive/10"
          >
            <Trash2 className="size-3.5" />
            Remove
          </button>
        </div>
      </header>

      {/* Detail cards */}
      <main className="flex-1 overflow-y-auto px-6 py-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-3xl">
          <section className="rounded-xl border border-border bg-card p-5 space-y-3">
            <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">
              Personal info
            </h2>
            <Row label="Full name" value={`${student.first_name} ${student.last_name}`} />
            <Row label="Gender" value={student.gender === "M" ? "Male" : "Female"} />
            <Row label="Date of birth" value={student.birth_date} />
            <Row label="Place of birth" value={student.birth_place} />
            {student.id_number && <Row label="ID / Extrait" value={student.id_number} />}
          </section>

          <section className="rounded-xl border border-border bg-card p-5 space-y-3">
            <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">
              Enrollment
            </h2>
            <Row label="Matricule" value={student.matricule} />
            <Row label="Class" value={student.class_id ?? "—"} />
            <Row label="Academic year" value={student.academic_year_id ?? "—"} />
            {student.created_at && (
              <Row
                label="Enrolled"
                value={new Date(student.created_at).toLocaleDateString()}
              />
            )}
          </section>
        </div>

      </main>

      {/* Edit modal */}
      {editOpen && (
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="edit-modal-title"
          className="fixed inset-0 z-50 flex items-center justify-center"
        >
          <div
            className="absolute inset-0 bg-black/50"
            onClick={handleEditClose}
            aria-hidden
          />
          <div className="relative z-10 w-full max-w-2xl rounded-xl border border-border bg-card shadow-xl max-h-[90vh] flex flex-col">
            <div className="flex items-center justify-between px-6 py-4 border-b border-border shrink-0">
              <h2 id="edit-modal-title" className="text-base font-semibold">
                Edit student
              </h2>
              <button
                aria-label="Close"
                onClick={handleEditClose}
                className="rounded p-1 text-muted-foreground hover:text-foreground"
              >
                <X className="size-4" />
              </button>
            </div>

            <form
              onSubmit={handleSubmit(onSubmit)}
              noValidate
              className="flex flex-col flex-1 overflow-hidden"
            >
              <div className="px-6 py-5 overflow-y-auto flex-1 space-y-6">
                {serverError && (
                  <div
                    role="alert"
                    className="rounded-lg border border-destructive/50 bg-destructive/10 px-4 py-3 text-sm text-destructive"
                  >
                    {serverError}
                  </div>
                )}

                <div>
                  <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-3">
                    Personal information
                  </p>
                  <div className="grid grid-cols-3 gap-4">
                    <FormField label="First name" name="first_name" error={errors.first_name} required>
                      <input className={inputClass} {...register("first_name")} />
                    </FormField>

                    <FormField label="Last name" name="last_name" error={errors.last_name} required>
                      <input className={inputClass} {...register("last_name")} />
                    </FormField>

                    <FormField label="Gender" name="gender" error={errors.gender} required>
                      <select className={inputClass} {...register("gender")}>
                        <option value="M">Male</option>
                        <option value="F">Female</option>
                      </select>
                    </FormField>

                    <FormField label="Date of birth" name="birth_date" error={errors.birth_date} required>
                      <Controller
                        name="birth_date"
                        control={control}
                        render={({ field }) => (
                          <DatePicker value={field.value} onChange={field.onChange} />
                        )}
                      />
                    </FormField>

                    <FormField label="Place of birth" name="birth_place" error={errors.birth_place} required className="col-span-2">
                      <input className={inputClass} {...register("birth_place")} />
                    </FormField>
                  </div>
                </div>

                <div>
                  <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-3">
                    Enrollment
                  </p>
                  <div className="grid grid-cols-2 gap-4">
                    <FormField label="Status" name="is_active">
                      <select className={inputClass} {...register("is_active", { setValueAs: (v) => v === "true" })}>
                        <option value="true">Active</option>
                        <option value="false">Inactive</option>
                      </select>
                    </FormField>

                    <FormField
                      label="ID / Extrait number"
                      name="id_number"
                      error={errors.id_number}
                    >
                      <input className={inputClass} {...register("id_number")} />
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
                  </div>
                </div>
              </div>

              <div className="flex justify-end gap-3 px-6 py-4 border-t border-border shrink-0">
                <button
                  type="button"
                  onClick={handleEditClose}
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
                  {busy ? "Saving…" : "Save changes"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      <ConfirmDialog
        open={deleteOpen}
        onOpenChange={(open) => { if (!isDeleting) setDeleteOpen(open); }}
        title="Remove student"
        description={
          deleteError
            ? deleteError
            : `Remove ${student.first_name} ${student.last_name} (${student.matricule})? This can be undone by an administrator.`
        }
        confirmLabel="Remove"
        isDestructive
        isLoading={isDeleting}
        onConfirm={handleDelete}
      />
    </>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between text-sm gap-4">
      <span className="text-muted-foreground shrink-0">{label}</span>
      <span className="font-medium text-right">{value}</span>
    </div>
  );
}

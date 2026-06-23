"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { type ColumnDef } from "@tanstack/react-table";
import { z } from "zod";

import { AdminShell } from "@/components/admin/AdminShell";
import { Button } from "@/components/ui/button";
import { DataTable } from "@/components/ui/DataTable";
import { FormField } from "@/components/ui/FormField";
import { getCsrfToken } from "@/lib/client/csrf";
import {
  AcademicYearCreateSchema,
  SchoolCreateSchema,
  type AcademicYearCreateValues,
  type AcademicYearRecord,
  type SchoolCreateValues,
  type SchoolRecord,
} from "@/lib/types/core";

const ChangePasswordSchema = z
  .object({
    old_password: z.string().min(1, "Current password is required."),
    new_password: z.string().min(8, "New password must be at least 8 characters."),
    confirm_password: z.string().min(1, "Confirm your new password."),
  })
  .refine((values) => values.new_password === values.confirm_password, {
    message: "Passwords do not match.",
    path: ["confirm_password"],
  });

type ChangePasswordValues = z.infer<typeof ChangePasswordSchema>;

async function fetchSchools(): Promise<SchoolRecord[]> {
  const response = await fetch("/api/admin/schools");
  if (!response.ok) throw new Error("Unable to load schools.");
  return (await response.json()) as SchoolRecord[];
}

async function fetchAcademicYears(): Promise<AcademicYearRecord[]> {
  const response = await fetch("/api/admin/academic-years");
  if (!response.ok) throw new Error("Unable to load academic years.");
  return (await response.json()) as AcademicYearRecord[];
}

const schoolColumns: ColumnDef<SchoolRecord>[] = [
  { accessorKey: "name", header: "Name" },
  { accessorKey: "code", header: "Code" },
  { accessorKey: "email", header: "Email", cell: ({ getValue }) => (getValue() as string) || "—" },
  {
    accessorKey: "is_active",
    header: "Status",
    cell: ({ getValue }) => ((getValue() as boolean | undefined) === false ? "Inactive" : "Active"),
  },
];

const yearColumns: ColumnDef<AcademicYearRecord>[] = [
  { accessorKey: "name", header: "Name" },
  { accessorKey: "start_date", header: "Start" },
  { accessorKey: "end_date", header: "End" },
  {
    accessorKey: "is_active",
    header: "Active",
    cell: ({ getValue }) => ((getValue() as boolean | undefined) ? "Yes" : "No"),
  },
];

export default function SettingsPage() {
  const queryClient = useQueryClient();
  const [tab, setTab] = useState<"schools" | "years" | "security">("schools");

  const schoolsQuery = useQuery({ queryKey: ["admin", "schools"], queryFn: fetchSchools });
  const yearsQuery = useQuery({
    queryKey: ["admin", "academic-years"],
    queryFn: fetchAcademicYears,
  });

  const schoolForm = useForm<SchoolCreateValues>({
    resolver: zodResolver(SchoolCreateSchema),
    defaultValues: { is_active: true },
  });
  const yearForm = useForm<AcademicYearCreateValues>({
    resolver: zodResolver(AcademicYearCreateSchema),
    defaultValues: { is_active: false },
  });
  const passwordForm = useForm<ChangePasswordValues>({
    resolver: zodResolver(ChangePasswordSchema),
  });

  const createSchool = useMutation({
    mutationFn: async (values: SchoolCreateValues) => {
      const response = await fetch("/api/admin/schools", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(values),
      });
      const payload = (await response.json()) as { error?: string };
      if (!response.ok) throw new Error(payload.error ?? "Unable to create school.");
    },
    onSuccess: () => {
      schoolForm.reset({ is_active: true });
      void queryClient.invalidateQueries({ queryKey: ["admin", "schools"] });
    },
  });

  const createYear = useMutation({
    mutationFn: async (values: AcademicYearCreateValues) => {
      const response = await fetch("/api/admin/academic-years", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(values),
      });
      const payload = (await response.json()) as { error?: string };
      if (!response.ok) throw new Error(payload.error ?? "Unable to create academic year.");
    },
    onSuccess: () => {
      yearForm.reset({ is_active: false });
      void queryClient.invalidateQueries({ queryKey: ["admin", "academic-years"] });
    },
  });

  const changePassword = useMutation({
    mutationFn: async (values: ChangePasswordValues) => {
      const response = await fetch("/api/auth/change-password", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRF-Token": getCsrfToken(),
        },
        body: JSON.stringify(values),
      });
      const payload = (await response.json()) as { detail?: string; error?: string };
      if (!response.ok) throw new Error(payload.error ?? payload.detail ?? "Unable to change password.");
    },
    onSuccess: () => passwordForm.reset(),
  });

  return (
    <AdminShell title="Settings" description="School configuration and account security">
      <div className="flex gap-2 mb-6">
        <Button type="button" variant={tab === "schools" ? "default" : "outline"} size="sm" onClick={() => setTab("schools")}>
          Schools
        </Button>
        <Button type="button" variant={tab === "years" ? "default" : "outline"} size="sm" onClick={() => setTab("years")}>
          Academic years
        </Button>
        <Button type="button" variant={tab === "security" ? "default" : "outline"} size="sm" onClick={() => setTab("security")}>
          Security
        </Button>
      </div>

      {tab === "schools" ? (
        <div className="grid gap-6 lg:grid-cols-[1fr_360px]">
          <DataTable data={schoolsQuery.data ?? []} columns={schoolColumns} filterPlaceholder="Search schools…" exportFilename="schools.csv" />
          <form onSubmit={schoolForm.handleSubmit((values) => createSchool.mutate(values))} className="space-y-3 rounded-xl border border-border bg-card p-5 h-fit">
            <h2 className="text-sm font-semibold">New school</h2>
            <FormField label="Name" name="name" error={schoolForm.formState.errors.name} required>
              <input className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm" {...schoolForm.register("name")} />
            </FormField>
            <FormField label="Code" name="code" error={schoolForm.formState.errors.code} required>
              <input className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm" {...schoolForm.register("code")} />
            </FormField>
            <FormField label="Email" name="email" error={schoolForm.formState.errors.email}>
              <input type="email" className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm" {...schoolForm.register("email")} />
            </FormField>
            <Button type="submit" disabled={createSchool.isPending} className="w-full">
              {createSchool.isPending ? "Creating…" : "Create school"}
            </Button>
          </form>
        </div>
      ) : null}

      {tab === "years" ? (
        <div className="grid gap-6 lg:grid-cols-[1fr_360px]">
          <DataTable data={yearsQuery.data ?? []} columns={yearColumns} filterPlaceholder="Search years…" exportFilename="academic-years.csv" />
          <form onSubmit={yearForm.handleSubmit((values) => createYear.mutate(values))} className="space-y-3 rounded-xl border border-border bg-card p-5 h-fit">
            <h2 className="text-sm font-semibold">New academic year</h2>
            <FormField label="Name" name="name" error={yearForm.formState.errors.name} required>
              <input className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm" {...yearForm.register("name")} />
            </FormField>
            <FormField label="Start date" name="start_date" error={yearForm.formState.errors.start_date} required>
              <input type="date" className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm" {...yearForm.register("start_date")} />
            </FormField>
            <FormField label="End date" name="end_date" error={yearForm.formState.errors.end_date} required>
              <input type="date" className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm" {...yearForm.register("end_date")} />
            </FormField>
            <label className="flex items-center gap-2 text-sm">
              <input type="checkbox" {...yearForm.register("is_active")} />
              Set as active year
            </label>
            <Button type="submit" disabled={createYear.isPending} className="w-full">
              {createYear.isPending ? "Creating…" : "Create academic year"}
            </Button>
          </form>
        </div>
      ) : null}

      {tab === "security" ? (
        <form
          onSubmit={passwordForm.handleSubmit((values) => changePassword.mutate(values))}
          className="max-w-md space-y-4 rounded-xl border border-border bg-card p-6"
        >
          <h2 className="text-sm font-semibold">Change password</h2>
          {changePassword.isSuccess ? (
            <p className="text-sm text-green-700 dark:text-green-300" role="status">
              Password updated successfully.
            </p>
          ) : null}
          {changePassword.error ? (
            <p className="text-sm text-destructive" role="alert">
              {changePassword.error instanceof Error
                ? changePassword.error.message
                : "Unable to change password."}
            </p>
          ) : null}
          <FormField label="Current password" name="old_password" error={passwordForm.formState.errors.old_password} required>
            <input type="password" className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm" {...passwordForm.register("old_password")} />
          </FormField>
          <FormField label="New password" name="new_password" error={passwordForm.formState.errors.new_password} required>
            <input type="password" className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm" {...passwordForm.register("new_password")} />
          </FormField>
          <FormField label="Confirm password" name="confirm_password" error={passwordForm.formState.errors.confirm_password} required>
            <input type="password" className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm" {...passwordForm.register("confirm_password")} />
          </FormField>
          <Button type="submit" disabled={changePassword.isPending}>
            {changePassword.isPending ? "Updating…" : "Update password"}
          </Button>
        </form>
      ) : null}
    </AdminShell>
  );
}

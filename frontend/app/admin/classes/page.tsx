"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { type ColumnDef } from "@tanstack/react-table";

import { AdminShell } from "@/components/admin/AdminShell";
import { Button } from "@/components/ui/button";
import { DataTable } from "@/components/ui/DataTable";
import { FormField } from "@/components/ui/FormField";
import type { AcademicYearRecord } from "@/lib/types/core";
import {
  ClassCreateSchema,
  SubjectCreateSchema,
  type ClassCreateValues,
  type ClassRecord,
  type SubjectCreateValues,
  type SubjectRecord,
} from "@/lib/types/classes";

async function fetchClasses(): Promise<ClassRecord[]> {
  const response = await fetch("/api/admin/classes");
  if (!response.ok) throw new Error("Unable to load classes.");
  return (await response.json()) as ClassRecord[];
}

async function fetchSubjects(): Promise<SubjectRecord[]> {
  const response = await fetch("/api/admin/subjects");
  if (!response.ok) throw new Error("Unable to load subjects.");
  return (await response.json()) as SubjectRecord[];
}

async function fetchAcademicYears(): Promise<AcademicYearRecord[]> {
  const response = await fetch("/api/admin/academic-years");
  if (!response.ok) throw new Error("Unable to load academic years.");
  return (await response.json()) as AcademicYearRecord[];
}

const classColumns: ColumnDef<ClassRecord>[] = [
  { accessorKey: "name", header: "Name" },
  { accessorKey: "level_id", header: "Level" },
  { accessorKey: "academic_year_id", header: "Academic year" },
  { accessorKey: "teacher_id", header: "Teacher ID", cell: ({ getValue }) => (getValue() as string) || "—" },
  { accessorKey: "capacity", header: "Capacity", cell: ({ getValue }) => String(getValue() ?? "—") },
];

const subjectColumns: ColumnDef<SubjectRecord>[] = [
  { accessorKey: "name", header: "Name" },
  { accessorKey: "code", header: "Code" },
  { accessorKey: "coefficient", header: "Coefficient" },
  { accessorKey: "class_id", header: "Class", cell: ({ getValue }) => (getValue() as string) || "—" },
];

export default function ClassesPage() {
  const queryClient = useQueryClient();
  const [tab, setTab] = useState<"classes" | "subjects">("classes");

  const classesQuery = useQuery({ queryKey: ["admin", "classes"], queryFn: fetchClasses });
  const subjectsQuery = useQuery({ queryKey: ["admin", "subjects"], queryFn: fetchSubjects });
  const yearsQuery = useQuery({
    queryKey: ["admin", "academic-years"],
    queryFn: fetchAcademicYears,
  });

  const classForm = useForm<ClassCreateValues>({
    resolver: zodResolver(ClassCreateSchema),
  });
  const subjectForm = useForm<SubjectCreateValues>({
    resolver: zodResolver(SubjectCreateSchema),
    defaultValues: { coefficient: 1 },
  });

  const createClass = useMutation({
    mutationFn: async (values: ClassCreateValues) => {
      const response = await fetch("/api/admin/classes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(values),
      });
      const payload = (await response.json()) as { error?: string };
      if (!response.ok) throw new Error(payload.error ?? "Unable to create class.");
    },
    onSuccess: () => {
      classForm.reset();
      void queryClient.invalidateQueries({ queryKey: ["admin", "classes"] });
    },
  });

  const createSubject = useMutation({
    mutationFn: async (values: SubjectCreateValues) => {
      const response = await fetch("/api/admin/subjects", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(values),
      });
      const payload = (await response.json()) as { error?: string };
      if (!response.ok) throw new Error(payload.error ?? "Unable to create subject.");
    },
    onSuccess: () => {
      subjectForm.reset({ coefficient: 1 });
      void queryClient.invalidateQueries({ queryKey: ["admin", "subjects"] });
    },
  });

  return (
    <AdminShell
      title="Classes"
      description="Manage classes, levels, and subjects"
    >
      <div className="flex gap-2 mb-6">
        <Button
          type="button"
          variant={tab === "classes" ? "default" : "outline"}
          size="sm"
          onClick={() => setTab("classes")}
        >
          Classes
        </Button>
        <Button
          type="button"
          variant={tab === "subjects" ? "default" : "outline"}
          size="sm"
          onClick={() => setTab("subjects")}
        >
          Subjects
        </Button>
      </div>

      {tab === "classes" ? (
        <div className="grid gap-6 lg:grid-cols-[1fr_360px]">
          <DataTable
            data={classesQuery.data ?? []}
            columns={classColumns}
            filterPlaceholder="Search classes…"
            exportFilename="classes.csv"
          />
          <form
            onSubmit={classForm.handleSubmit((values) => createClass.mutate(values))}
            className="space-y-3 rounded-xl border border-border bg-card p-5 h-fit"
          >
            <h2 className="text-sm font-semibold">New class</h2>
            <FormField label="Name" name="name" error={classForm.formState.errors.name} required>
              <input className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm" {...classForm.register("name")} />
            </FormField>
            <FormField label="Level ID" name="level_id" error={classForm.formState.errors.level_id} required>
              <input className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm" {...classForm.register("level_id")} />
            </FormField>
            <FormField label="Academic year" name="academic_year_id" error={classForm.formState.errors.academic_year_id} required>
              <select className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm" {...classForm.register("academic_year_id")}>
                <option value="">Select year</option>
                {(yearsQuery.data ?? []).map((year) => (
                  <option key={year.id} value={year.id}>{year.name}</option>
                ))}
              </select>
            </FormField>
            <FormField label="Teacher ID" name="teacher_id" error={classForm.formState.errors.teacher_id}>
              <input className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm" {...classForm.register("teacher_id")} />
            </FormField>
            <FormField label="Capacity" name="capacity" error={classForm.formState.errors.capacity}>
              <input
                type="number"
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                {...classForm.register("capacity", { valueAsNumber: true })}
              />
            </FormField>
            <Button type="submit" disabled={createClass.isPending} className="w-full">
              {createClass.isPending ? "Creating…" : "Create class"}
            </Button>
          </form>
        </div>
      ) : (
        <div className="grid gap-6 lg:grid-cols-[1fr_360px]">
          <DataTable
            data={subjectsQuery.data ?? []}
            columns={subjectColumns}
            filterPlaceholder="Search subjects…"
            exportFilename="subjects.csv"
          />
          <form
            onSubmit={subjectForm.handleSubmit((values) => createSubject.mutate(values))}
            className="space-y-3 rounded-xl border border-border bg-card p-5 h-fit"
          >
            <h2 className="text-sm font-semibold">New subject</h2>
            <FormField label="Name" name="name" error={subjectForm.formState.errors.name} required>
              <input className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm" {...subjectForm.register("name")} />
            </FormField>
            <FormField label="Code" name="code" error={subjectForm.formState.errors.code} required>
              <input className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm" {...subjectForm.register("code")} />
            </FormField>
            <FormField label="Coefficient" name="coefficient" error={subjectForm.formState.errors.coefficient} required>
              <input
                type="number"
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                {...subjectForm.register("coefficient", { valueAsNumber: true })}
              />
            </FormField>
            <FormField label="Class ID" name="class_id" error={subjectForm.formState.errors.class_id}>
              <input className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm" {...subjectForm.register("class_id")} />
            </FormField>
            <Button type="submit" disabled={createSubject.isPending} className="w-full">
              {createSubject.isPending ? "Creating…" : "Create subject"}
            </Button>
          </form>
        </div>
      )}
    </AdminShell>
  );
}

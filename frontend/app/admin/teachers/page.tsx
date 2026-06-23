"use client";

import { useQuery } from "@tanstack/react-query";
import { type ColumnDef } from "@tanstack/react-table";

import { AdminShell } from "@/components/admin/AdminShell";
import { DataTable } from "@/components/ui/DataTable";
import type { ClassRecord } from "@/lib/types/classes";

async function fetchClasses(): Promise<ClassRecord[]> {
  const response = await fetch("/api/admin/classes");
  if (!response.ok) throw new Error("Unable to load classes.");
  return (await response.json()) as ClassRecord[];
}

const columns: ColumnDef<ClassRecord>[] = [
  { accessorKey: "name", header: "Class" },
  { accessorKey: "teacher_id", header: "Teacher ID", cell: ({ getValue }) => (getValue() as string) || "Unassigned" },
  { accessorKey: "level_id", header: "Level" },
  { accessorKey: "capacity", header: "Capacity", cell: ({ getValue }) => String(getValue() ?? "—") },
];

const unassignedColumns: ColumnDef<ClassRecord>[] = [
  { accessorKey: "name", header: "Class" },
  { accessorKey: "level_id", header: "Level" },
  { accessorKey: "capacity", header: "Capacity", cell: ({ getValue }) => String(getValue() ?? "—") },
];

export default function TeachersPage() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["admin", "classes"],
    queryFn: fetchClasses,
  });

  const assigned = (data ?? []).filter((item) => item.teacher_id?.trim());
  const unassigned = (data ?? []).filter((item) => !item.teacher_id?.trim());

  return (
    <AdminShell
      title="Teachers"
      description="Teacher assignments are managed via class teacher_id"
    >
      <div className="rounded-xl border border-amber-200 bg-amber-50 dark:border-amber-900/40 dark:bg-amber-900/20 px-4 py-3 text-sm text-amber-900 dark:text-amber-200 mb-6">
        There is no dedicated teachers API yet. Assign a teacher by setting the
        <code className="mx-1 rounded bg-background/60 px-1">teacher_id</code>
        field when creating or editing a class under Classes.
      </div>

      {error ? (
        <p className="text-sm text-destructive">Unable to load class assignments.</p>
      ) : isLoading ? (
        <p className="text-sm text-muted-foreground">Loading assignments…</p>
      ) : (
        <div className="space-y-6">
          <section>
            <h2 className="text-sm font-semibold mb-3">
              Assigned ({assigned.length})
            </h2>
            <DataTable
              data={assigned}
              columns={columns}
              filterPlaceholder="Search assignments…"
              exportFilename="teacher-assignments.csv"
            />
          </section>

          <section>
            <h2 className="text-sm font-semibold mb-3">
              Unassigned classes ({unassigned.length})
            </h2>
            <DataTable
              data={unassigned}
              columns={unassignedColumns}
              filterPlaceholder="Search classes…"
              exportFilename="unassigned-classes.csv"
            />
          </section>
        </div>
      )}
    </AdminShell>
  );
}

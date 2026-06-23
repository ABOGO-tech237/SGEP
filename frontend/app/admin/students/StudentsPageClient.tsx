"use client";

import { useMemo } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { type ColumnDef } from "@tanstack/react-table";
import Link from "next/link";
import { Plus } from "lucide-react";

import { AdminShell } from "@/components/admin/AdminShell";
import { Button } from "@/components/ui/button";
import { DataTable } from "@/components/ui/DataTable";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { buildNameLookup, lookupName } from "@/lib/lookups";
import type { ClassRecord } from "@/lib/types/classes";
import type { StudentListItem, StudentsListResponse } from "@/lib/types/students";

async function fetchStudents(): Promise<StudentsListResponse> {
  const response = await fetch("/api/admin/students?page_size=100");
  if (!response.ok) {
    throw new Error("Unable to load students.");
  }
  return (await response.json()) as StudentsListResponse;
}

async function fetchClasses(): Promise<ClassRecord[]> {
  const response = await fetch("/api/admin/classes");
  if (!response.ok) throw new Error("Unable to load classes.");
  return (await response.json()) as ClassRecord[];
}

export default function StudentsPageClient() {
  const queryClient = useQueryClient();
  const { data, isLoading, error } = useQuery({
    queryKey: ["admin", "students"],
    queryFn: fetchStudents,
  });
  const classesQuery = useQuery({
    queryKey: ["admin", "classes"],
    queryFn: fetchClasses,
  });

  const classNames = useMemo(
    () => buildNameLookup(classesQuery.data ?? []),
    [classesQuery.data],
  );

  const columns = useMemo<ColumnDef<StudentListItem>[]>(
    () => [
      {
        accessorKey: "matricule",
        header: "Matricule",
      },
      {
        id: "name",
        header: "Name",
        accessorFn: (row) => `${row.first_name} ${row.last_name}`,
        cell: ({ row }) => (
          <Link
            href={`/admin/students/${row.original.id}`}
            className="font-medium hover:underline"
          >
            {row.original.first_name} {row.original.last_name}
          </Link>
        ),
      },
      {
        id: "class",
        header: "Class",
        accessorFn: (row) =>
          lookupName(classNames, row.class_id, row.class_id ?? "Unassigned"),
        cell: ({ row }) =>
          lookupName(classNames, row.original.class_id, row.original.class_id ?? "Unassigned"),
      },
      {
        id: "status",
        header: "Status",
        cell: ({ row }) => (
          <StatusBadge status={row.original.is_active === false ? "SUSPENDED" : "ACTIVE"} />
        ),
      },
    ],
    [classNames],
  );

  const refresh = useMutation({
    mutationFn: fetchStudents,
    onSuccess: (result) => {
      queryClient.setQueryData(["admin", "students"], result);
    },
  });

  return (
    <AdminShell
      title="Students"
      description={
        data
          ? `${data.total} student records`
          : isLoading
            ? "Loading students…"
            : "Student registry"
      }
      actions={
        <Link
          href="/admin/students/new"
          className="inline-flex h-7 items-center gap-1 rounded-[min(var(--radius-md),12px)] bg-primary px-2.5 text-[0.8rem] font-medium text-primary-foreground transition hover:bg-primary/80"
        >
          <Plus className="size-3.5" />
          Add student
        </Link>
      }
    >
      {error ? (
        <div className="rounded-xl border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive">
          {error instanceof Error ? error.message : "Unable to load students."}
        </div>
      ) : isLoading ? (
        <p className="text-sm text-muted-foreground">Loading students…</p>
      ) : (
        <DataTable
          data={data?.items ?? []}
          columns={columns}
          filterPlaceholder="Search students…"
          exportFilename="students.csv"
        />
      )}

      <div className="mt-4">
        <Button
          variant="outline"
          size="sm"
          disabled={refresh.isPending}
          onClick={() => refresh.mutate()}
        >
          Refresh list
        </Button>
      </div>
    </AdminShell>
  );
}

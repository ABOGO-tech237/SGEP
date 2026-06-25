"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { type ColumnDef } from "@tanstack/react-table";
import Link from "next/link";

import { AdminShell } from "@/components/admin/AdminShell";
import { EnrolStudentButton } from "./EnrolStudentButton";
import { Button } from "@/components/ui/button";
import { DataTable } from "@/components/ui/DataTable";
import { StatusBadge } from "@/components/ui/StatusBadge";
import type { StudentListItem, StudentsListResponse } from "@/lib/types/students";

async function fetchStudents(): Promise<StudentsListResponse> {
  const response = await fetch("/api/admin/students?page_size=100");
  if (!response.ok) {
    throw new Error("Unable to load students.");
  }
  return (await response.json()) as StudentsListResponse;
}

const columns: ColumnDef<StudentListItem>[] = [
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
    accessorKey: "class_id",
    header: "Class",
    cell: ({ getValue }) => (getValue() as string | null) || "Unassigned",
  },
  {
    id: "status",
    header: "Status",
    cell: ({ row }) => (
      <StatusBadge status={row.original.is_active === false ? "SUSPENDED" : "ACTIVE"} />
    ),
  },
];

export default function StudentsPageClient() {
  const queryClient = useQueryClient();
  const { data, isLoading, error } = useQuery({
    queryKey: ["admin", "students"],
    queryFn: fetchStudents,
  });

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
        <div className="flex items-center gap-2">
          <EnrolStudentButton />
          <Link
            href="/admin/students/new"
            className="inline-flex h-7 items-center rounded-[min(var(--radius-md),12px)] border border-input bg-background px-2.5 text-[0.8rem] font-medium transition hover:bg-muted"
          >
            Full form
          </Link>
        </div>
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

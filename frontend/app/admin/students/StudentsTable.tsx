"use client";

import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";
import { type ColumnDef } from "@tanstack/react-table";
import { Pencil, Trash2 } from "lucide-react";
import { DataTable } from "@/components/ui/DataTable";
import { ConfirmDialog } from "@/components/ui/ConfirmDialog";
import type { StudentListItem } from "@/lib/types/students";

const statusCell = (active: boolean | undefined) => (
  <span
    className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${
      active
        ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-900/20 dark:text-emerald-400"
        : "bg-muted text-muted-foreground"
    }`}
  >
    {active ? "Active" : "Inactive"}
  </span>
);

interface StudentsTableProps {
  students: StudentListItem[];
}

export function StudentsTable({ students }: StudentsTableProps) {
  const router = useRouter();
  const [, startTransition] = useTransition();
  const [deleteTarget, setDeleteTarget] = useState<StudentListItem | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  async function handleDelete() {
    if (!deleteTarget) return;
    setIsDeleting(true);
    setDeleteError(null);

    try {
      const res = await fetch(`/api/students/${deleteTarget.id}`, {
        method: "DELETE",
      });

      if (!res.ok) {
        const body: unknown = await res.json().catch(() => ({}));
        const b = body as Record<string, unknown>;
        const msg =
          typeof b.detail === "string" ? b.detail :
          typeof b.error === "string" ? b.error :
          typeof b.message === "string" ? b.message :
          "Could not delete student. Please try again.";
        setDeleteError(msg);
        return;
      }

      setDeleteTarget(null);
      setDeleteError(null);
      startTransition(() => router.refresh());
    } finally {
      setIsDeleting(false);
    }
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
    },
    {
      accessorKey: "class_id",
      header: "Class",
      cell: ({ getValue }) => (getValue<string | null>() ?? "—"),
    },
    {
      accessorKey: "is_active",
      header: "Status",
      cell: ({ getValue }) => statusCell(getValue<boolean | undefined>()),
    },
    {
      id: "actions",
      header: "",
      cell: ({ row }) => (
        <div className="flex items-center justify-end gap-1">
          <button
            aria-label="Edit student"
            className="rounded p-1.5 text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
            onClick={() => router.push(`/admin/students/${row.original.id}`)}
          >
            <Pencil className="size-3.5" />
          </button>
          <button
            aria-label="Delete student"
            className="rounded p-1.5 text-muted-foreground hover:bg-destructive/10 hover:text-destructive transition-colors"
            onClick={() => { setDeleteError(null); setDeleteTarget(row.original); }}
          >
            <Trash2 className="size-3.5" />
          </button>
        </div>
      ),
      enableSorting: false,
    },
  ];

  return (
    <>
      <DataTable
        data={students}
        columns={columns}
        filterPlaceholder="Search students…"
        exportFilename="students.csv"
      />

      <ConfirmDialog
        open={!!deleteTarget}
        onOpenChange={(open) => {
          if (!open && !isDeleting) {
            setDeleteTarget(null);
            setDeleteError(null);
          }
        }}
        title="Remove student"
        description={
          deleteError
            ? deleteError
            : deleteTarget
              ? `Remove ${deleteTarget.first_name} ${deleteTarget.last_name} (${deleteTarget.matricule})?`
              : ""
        }
        confirmLabel="Remove"
        isDestructive
        isLoading={isDeleting}
        onConfirm={handleDelete}
      />
    </>
  );
}

"use client";

import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";

import { AdminShell } from "@/components/admin/AdminShell";
import { ExportJobPoller } from "@/components/admin/ExportJobPoller";
import { Button } from "@/components/ui/button";
import type { ClassRecord } from "@/lib/types/classes";
import type { ExportJobResponse } from "@/lib/types/reports";

interface ActiveJob {
  id: string;
  label: string;
  statusPath: "reports" | "report-cards";
}

async function fetchClasses(): Promise<ClassRecord[]> {
  const response = await fetch("/api/admin/classes");
  if (!response.ok) throw new Error("Unable to load classes.");
  return (await response.json()) as ClassRecord[];
}

export default function ReportsPage() {
  const [classId, setClassId] = useState("");
  const [periodId, setPeriodId] = useState("");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [jobs, setJobs] = useState<ActiveJob[]>([]);

  const classesQuery = useQuery({ queryKey: ["admin", "classes"], queryFn: fetchClasses });

  const startJob = useMutation({
    mutationFn: async ({
      url,
      label,
      statusPath,
      method = "GET",
      body,
    }: {
      url: string;
      label: string;
      statusPath: "reports" | "report-cards";
      method?: "GET" | "POST";
      body?: Record<string, string>;
    }) => {
      const response = await fetch(url, {
        method,
        headers: body ? { "Content-Type": "application/json" } : undefined,
        body: body ? JSON.stringify(body) : undefined,
      });
      const payload = (await response.json()) as ExportJobResponse & { error?: string };
      if (!response.ok) throw new Error(payload.error ?? "Unable to start export.");
      return { jobId: payload.job_id, label, statusPath };
    },
    onSuccess: ({ jobId, label, statusPath }) => {
      setJobs((current) => [{ id: jobId, label, statusPath }, ...current]);
    },
  });

  return (
    <AdminShell title="Reports" description="Generate exports and report cards">
      <div className="grid gap-6 lg:grid-cols-2">
        <section className="rounded-xl border border-border bg-card p-5 space-y-4">
          <h2 className="text-sm font-semibold">Student exports</h2>
          <p className="text-xs text-muted-foreground">
            Export the full student registry as PDF or Excel.
          </p>
          <div className="flex flex-wrap gap-2">
            <Button
              type="button"
              variant="outline"
              disabled={startJob.isPending}
              onClick={() =>
                startJob.mutate({
                  url: "/api/admin/students/export/pdf",
                  label: "Students PDF export",
                  statusPath: "reports",
                })
              }
            >
              Export PDF
            </Button>
            <Button
              type="button"
              variant="outline"
              disabled={startJob.isPending}
              onClick={() =>
                startJob.mutate({
                  url: "/api/admin/students/export/excel",
                  label: "Students Excel export",
                  statusPath: "reports",
                })
              }
            >
              Export Excel
            </Button>
          </div>
        </section>

        <section className="rounded-xl border border-border bg-card p-5 space-y-4">
          <h2 className="text-sm font-semibold">Grade results</h2>
          <div className="grid gap-3">
            <label className="text-sm">
              <span className="block mb-1 text-muted-foreground">Class</span>
              <select
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                value={classId}
                onChange={(event) => setClassId(event.target.value)}
              >
                <option value="">Select class</option>
                {(classesQuery.data ?? []).map((item) => (
                  <option key={item.id} value={item.id}>{item.name}</option>
                ))}
              </select>
            </label>
            <label className="text-sm">
              <span className="block mb-1 text-muted-foreground">Period ID</span>
              <input
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                value={periodId}
                onChange={(event) => setPeriodId(event.target.value)}
                placeholder="e.g. T1"
              />
            </label>
            <Button
              type="button"
              disabled={!classId || !periodId || startJob.isPending}
              onClick={() =>
                startJob.mutate({
                  url: `/api/admin/grades/export/results?class_id=${encodeURIComponent(classId)}&period_id=${encodeURIComponent(periodId)}`,
                  label: "Grade results Excel",
                  statusPath: "reports",
                })
              }
            >
              Export results
            </Button>
          </div>
        </section>

        <section className="rounded-xl border border-border bg-card p-5 space-y-4">
          <h2 className="text-sm font-semibold">Report cards</h2>
          <div className="grid gap-3">
            <label className="text-sm">
              <span className="block mb-1 text-muted-foreground">Class</span>
              <select
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                value={classId}
                onChange={(event) => setClassId(event.target.value)}
              >
                <option value="">Select class</option>
                {(classesQuery.data ?? []).map((item) => (
                  <option key={item.id} value={item.id}>{item.name}</option>
                ))}
              </select>
            </label>
            <label className="text-sm">
              <span className="block mb-1 text-muted-foreground">Period ID</span>
              <input
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                value={periodId}
                onChange={(event) => setPeriodId(event.target.value)}
                placeholder="e.g. T1"
              />
            </label>
            <Button
              type="button"
              disabled={!classId || !periodId || startJob.isPending}
              onClick={() =>
                startJob.mutate({
                  url: "/api/admin/report-cards/generate",
                  label: "Report cards generation",
                  statusPath: "report-cards",
                  method: "POST",
                  body: { class_id: classId, period_id: periodId },
                })
              }
            >
              Generate report cards
            </Button>
          </div>
        </section>

        <section className="rounded-xl border border-border bg-card p-5 space-y-4">
          <h2 className="text-sm font-semibold">Attendance export</h2>
          <div className="grid gap-3">
            <label className="text-sm">
              <span className="block mb-1 text-muted-foreground">Class ID</span>
              <input
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                value={classId}
                onChange={(event) => setClassId(event.target.value)}
              />
            </label>
            <label className="text-sm">
              <span className="block mb-1 text-muted-foreground">Date from</span>
              <input
                type="date"
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                value={dateFrom}
                onChange={(event) => setDateFrom(event.target.value)}
              />
            </label>
            <label className="text-sm">
              <span className="block mb-1 text-muted-foreground">Date to</span>
              <input
                type="date"
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                value={dateTo}
                onChange={(event) => setDateTo(event.target.value)}
              />
            </label>
            <div className="flex gap-2">
              <Button
                type="button"
                variant="outline"
                disabled={!classId || !dateFrom || !dateTo || startJob.isPending}
                onClick={() =>
                  startJob.mutate({
                    url: `/api/admin/attendance/export?format=excel&class_id=${encodeURIComponent(classId)}&date_from=${encodeURIComponent(dateFrom)}&date_to=${encodeURIComponent(dateTo)}`,
                    label: "Attendance Excel export",
                    statusPath: "reports",
                  })
                }
              >
                Excel
              </Button>
              <Button
                type="button"
                variant="outline"
                disabled={!classId || !dateFrom || !dateTo || startJob.isPending}
                onClick={() =>
                  startJob.mutate({
                    url: `/api/admin/attendance/export?format=pdf&class_id=${encodeURIComponent(classId)}&date_from=${encodeURIComponent(dateFrom)}&date_to=${encodeURIComponent(dateTo)}`,
                    label: "Attendance PDF export",
                    statusPath: "reports",
                  })
                }
              >
                PDF
              </Button>
            </div>
          </div>
        </section>
      </div>

      {startJob.error ? (
        <p className="mt-6 text-sm text-destructive" role="alert">
          {startJob.error instanceof Error ? startJob.error.message : "Export failed."}
        </p>
      ) : null}

      {jobs.length > 0 ? (
        <div className="mt-6 space-y-3">
          <h2 className="text-sm font-semibold">Active jobs</h2>
          {jobs.map((job) => (
            <ExportJobPoller
              key={job.id}
              jobId={job.id}
              label={job.label}
              statusPath={job.statusPath}
            />
          ))}
        </div>
      ) : null}
    </AdminShell>
  );
}

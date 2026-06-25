import { describe, expect, it } from "vitest";

import { buildAdminDashboard } from "@/lib/admin";
import type { StudentRecord } from "@/lib/types/admin";

const students: StudentRecord[] = [
  {
    id: "stu-1",
    matricule: "S001",
    first_name: "Ada",
    last_name: "Mbia",
    class_id: "Grade 3A",
    academic_year_id: "2025-2026",
    is_active: true,
    created_at: "2026-06-01T08:00:00.000Z",
    updated_at: "2026-06-01T08:00:00.000Z",
  },
  {
    id: "stu-2",
    matricule: "S002",
    first_name: "Ben",
    last_name: "Tchamda",
    class_id: "Grade 3A",
    academic_year_id: "2025-2026",
    is_active: false,
    created_at: "2026-05-20T08:00:00.000Z",
    updated_at: "2026-05-30T08:00:00.000Z",
  },
  {
    id: "stu-3",
    matricule: "S003",
    first_name: "Cleo",
    last_name: "Nono",
    class_id: "Grade 4B",
    academic_year_id: "2025-2026",
    is_active: true,
    created_at: "2026-05-28T08:00:00.000Z",
    updated_at: "2026-05-28T08:00:00.000Z",
  },
  {
    id: "stu-4",
    matricule: "S004",
    first_name: "Dina",
    last_name: "Kone",
    class_id: null,
    academic_year_id: "2025-2026",
    is_active: true,
    created_at: "2026-06-01T09:00:00.000Z",
    updated_at: "2026-06-01T09:00:00.000Z",
  },
];

describe("buildAdminDashboard", () => {
  it("derives dashboard stats from live student records", () => {
    const dashboard = buildAdminDashboard(students, 4, new Date("2026-06-02T12:00:00.000Z"));

    expect(dashboard.stats).toHaveLength(4);
    expect(dashboard.stats[0]).toMatchObject({
      label: "Total Students",
      value: "4",
    });
    expect(dashboard.stats[1]).toMatchObject({
      label: "Active Students",
      value: "3",
    });
    expect(dashboard.stats[2]).toMatchObject({
      label: "Inactive Students",
      value: "1",
    });
    expect(dashboard.stats[3]).toMatchObject({
      label: "Classes Represented",
      value: "2",
    });
  });

  it("builds recent activity entries from the latest students", () => {
    const dashboard = buildAdminDashboard(students, 4, new Date("2026-06-02T12:00:00.000Z"));

    expect(dashboard.recent_activity).toHaveLength(4);
    expect(dashboard.recent_activity[0]).toMatchObject({
      name: "Ada Mbia",
      action: "Enrolled",
      grade: "Grade 3A",
      status: "PENDING",
    });
    expect(dashboard.recent_activity[1]).toMatchObject({
      name: "Ben Tchamda",
      action: "Suspended",
      status: "SUSPENDED",
    });
    expect(dashboard.recent_activity[3]).toMatchObject({
      name: "Dina Kone",
      action: "Awaiting class assignment",
      grade: "Unassigned",
      status: "PENDING",
    });
  });
});
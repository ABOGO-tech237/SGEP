import type {
  AdminDashboardActivity,
  AdminDashboardResponse,
  AdminDashboardStat,
  StudentRecord,
} from "@/lib/types/admin";

const RECENT_ACTIVITY_LIMIT = 5;
const RECENT_ACTIVITY_WINDOW_DAYS = 7;

function parseTimestamp(value?: string | null): number | null {
  if (!value) {
    return null;
  }

  const parsed = Date.parse(value);
  return Number.isNaN(parsed) ? null : parsed;
}

function formatCount(value: number): string {
  return new Intl.NumberFormat("en-US").format(value);
}

function formatPercent(value: number): string {
  return `${value.toFixed(1)}%`;
}

function formatRelativeTime(target: string | undefined, now: Date): string {
  const targetTimestamp = parseTimestamp(target);
  if (targetTimestamp === null) {
    return "just now";
  }

  const deltaMinutes = Math.round((now.getTime() - targetTimestamp) / 60000);
  if (deltaMinutes <= 0) {
    return "just now";
  }
  if (deltaMinutes < 60) {
    return `${deltaMinutes} min ago`;
  }

  const deltaHours = Math.round(deltaMinutes / 60);
  if (deltaHours < 24) {
    return `${deltaHours} hr ago`;
  }

  const deltaDays = Math.round(deltaHours / 24);
  if (deltaDays === 1) {
    return "Yesterday";
  }

  return `${deltaDays} days ago`;
}

function isWithinDays(target: string | undefined, now: Date, days: number): boolean {
  const targetTimestamp = parseTimestamp(target);
  if (targetTimestamp === null) {
    return false;
  }

  return now.getTime() - targetTimestamp <= days * 24 * 60 * 60 * 1000;
}

function buildActivity(student: StudentRecord, now: Date): AdminDashboardActivity {
  const createdAt = parseTimestamp(student.created_at);
  const updatedAt = parseTimestamp(student.updated_at);
  const deletedAt = parseTimestamp(student.deleted_at);

  let action = "Active record";
  let status: AdminDashboardActivity["status"] = "ACTIVE";
  let timeSource = student.updated_at ?? student.created_at;

  if (student.is_deleted || deletedAt !== null) {
    action = "Archived";
    status = "SUSPENDED";
    timeSource = student.deleted_at ?? student.updated_at ?? student.created_at;
  } else if (student.is_active === false) {
    action = "Suspended";
    status = "SUSPENDED";
  } else if (!student.class_id) {
    action = "Awaiting class assignment";
    status = "PENDING";
    timeSource = student.created_at;
  } else if (isWithinDays(student.created_at, now, RECENT_ACTIVITY_WINDOW_DAYS)) {
    action = "Enrolled";
    status = "PENDING";
    timeSource = student.created_at;
  } else if (
    createdAt !== null &&
    updatedAt !== null &&
    updatedAt > createdAt
  ) {
    action = "Profile updated";
    timeSource = student.updated_at;
  }

  return {
    id: student.id,
    name: `${student.first_name} ${student.last_name}`,
    action,
    grade: student.class_id?.trim() || "Unassigned",
    status,
    time: formatRelativeTime(timeSource, now),
  };
}

export function buildAdminDashboard(
  students: StudentRecord[],
  totalStudents: number,
  now = new Date(),
): AdminDashboardResponse {
  const activeStudents = students.filter(
    (student) => student.is_active !== false && !student.is_deleted,
  ).length;
  const inactiveStudents = Math.max(totalStudents - activeStudents, 0);
  const uniqueClasses = new Set(
    students
      .map((student) => student.class_id?.trim())
      .filter((classId): classId is string => Boolean(classId)),
  );
  const recentRegistrations = students.filter((student) =>
    isWithinDays(student.created_at, now, RECENT_ACTIVITY_WINDOW_DAYS),
  ).length;

  const stats: AdminDashboardStat[] = [
    {
      label: "Total Students",
      value: formatCount(totalStudents),
      change: "Live records from Appwrite",
      positive: null,
    },
    {
      label: "Active Students",
      value: formatCount(activeStudents),
      change:
        totalStudents > 0
          ? `${formatPercent((activeStudents / totalStudents) * 100)} active`
          : "No active records",
      positive: activeStudents <= totalStudents,
    },
    {
      label: "Inactive Students",
      value: formatCount(inactiveStudents),
      change:
        inactiveStudents === 0
          ? "No suspended records"
          : `${formatCount(inactiveStudents)} records need follow-up`,
      positive: inactiveStudents === 0,
    },
    {
      label: "Classes Represented",
      value: formatCount(uniqueClasses.size),
      change: `${formatCount(recentRegistrations)} recent registrations`,
      positive: null,
    },
  ];

  const recentActivity = students
    .slice(0, RECENT_ACTIVITY_LIMIT)
    .map((student) => buildActivity(student, now));

  return {
    generated_at: now.toISOString(),
    stats,
    recent_activity: recentActivity,
  };
}
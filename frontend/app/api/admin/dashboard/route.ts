import { NextResponse } from "next/server";

import { ApiError, proxyFetch } from "@/lib/server/proxy-fetch";
import { buildAdminDashboard } from "@/lib/admin";
import type { StudentsListResponse } from "@/lib/types/admin";

const STUDENTS_PAGE_SIZE = 100;

async function fetchStudentsPage(page: number): Promise<StudentsListResponse> {
  const response = await proxyFetch(
    `/students/?page=${page}&page_size=${STUDENTS_PAGE_SIZE}`,
  );

  if (!response.ok) {
    throw new Error(`Unable to load students dashboard data (${response.status})`);
  }

  return (await response.json()) as StudentsListResponse;
}

export async function GET(): Promise<Response> {
  try {
    const firstPage = await fetchStudentsPage(1);
    const totalStudents = firstPage.total ?? firstPage.items.length;
    const totalPages = Math.max(
      1,
      Math.ceil(totalStudents / STUDENTS_PAGE_SIZE),
    );

    const students = [...firstPage.items];
    for (let page = 2; page <= totalPages; page += 1) {
      const pageData = await fetchStudentsPage(page);
      students.push(...pageData.items);
    }

    const dashboard = buildAdminDashboard(students, totalStudents);
    return NextResponse.json(dashboard, {
      headers: {
        "Cache-Control": "no-store",
      },
    });
  } catch (error) {
    if (error instanceof ApiError) {
      return NextResponse.json({ error: error.message }, { status: error.status });
    }

    return NextResponse.json(
      { error: "Service unavailable." },
      { status: 503 },
    );
  }
}
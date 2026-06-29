import { describe, expect, it } from "vitest";

import { CreateStudentSchema } from "@/lib/types/students";

describe("CreateStudentSchema", () => {
  const validPayload = {
    first_name: "Awa",
    last_name: "Nana",
    birth_date: "2015-03-12",
    birth_place: "Douala",
    gender: "F",
    class_id: "class-1",
    academic_year_id: "year-1",
  };

  it("accepts payload without matricule", () => {
    const result = CreateStudentSchema.safeParse(validPayload);
    expect(result.success).toBe(true);
  });

  it("accepts an optional user-provided matricule", () => {
    const result = CreateStudentSchema.safeParse({ ...validPayload, matricule: "2026-001" });
    expect(result.success).toBe(true);
  });

  it("accepts empty matricule", () => {
    const result = CreateStudentSchema.safeParse({ ...validPayload, matricule: "" });
    expect(result.success).toBe(true);
  });
});

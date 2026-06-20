import { z } from "zod";

export interface ClassRecord {
  id: string;
  name: string;
  level_id: string;
  academic_year_id: string;
  school_id?: string;
  capacity?: number | null;
  teacher_id?: string;
}

export interface SubjectRecord {
  id: string;
  name: string;
  code: string;
  coefficient: number;
  class_id?: string;
  level_id?: string;
}

export const ClassCreateSchema = z.object({
  name: z.string().min(1, "Name is required."),
  level_id: z.string().min(1, "Level is required."),
  academic_year_id: z.string().min(1, "Academic year is required."),
  school_id: z.string().optional(),
  capacity: z.number().int().positive().optional().nullable(),
  teacher_id: z.string().optional(),
});

export type ClassCreateValues = z.infer<typeof ClassCreateSchema>;

export const SubjectCreateSchema = z.object({
  name: z.string().min(1, "Name is required."),
  code: z.string().min(1, "Code is required."),
  coefficient: z.number().int().min(1, "Coefficient must be at least 1."),
  class_id: z.string().optional(),
  level_id: z.string().optional(),
});

export type SubjectCreateValues = z.infer<typeof SubjectCreateSchema>;
